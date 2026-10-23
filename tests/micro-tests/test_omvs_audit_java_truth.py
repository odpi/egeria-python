"""
omvs_audit's Java ground truth (ISSUE-163): endpoint -> @RequestBody index, the
polymorphic-base rule that decides REJECTED vs CLASS-IGNORED, and the class-name
scan. Runs against a tiny synthetic Java tree, not a real Egeria checkout.
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import omvs_audit  # noqa: E402

FILES = {
    "frameworks/x/src/main/java/rest/DeleteRequestBody.java": """
        @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "class")
        @JsonSubTypes({@JsonSubTypes.Type(value = DeleteElementRequestBody.class, name = "DeleteElementRequestBody")})
        public class DeleteRequestBody extends DeleteOptions {}
    """,
    "frameworks/x/src/main/java/rest/DeleteElementRequestBody.java":
        "public class DeleteElementRequestBody extends DeleteRequestBody {}",
    "frameworks/x/src/main/java/rest/DeleteRelationshipRequestBody.java":
        "public class DeleteRelationshipRequestBody extends DeleteRequestBody {}",
    "frameworks/x/src/main/java/rest/ResultsRequestBody.java":
        "public class ResultsRequestBody extends QueryOptions {}",
    "frameworks/x/src/main/java/rest/FilterRequestBody.java":
        "public class FilterRequestBody extends QueryOptions {}",
    "frameworks/x/src/main/java/properties/PersonRoleAppointmentProperties.java":
        "public class PersonRoleAppointmentProperties extends RelationshipBeanProperties {}",
    "view/actor-manager-spring/src/main/java/server/spring/ActorManagerResource.java": """
        @RequestMapping("/servers/{serverName}/api/open-metadata/{urlMarker}")
        public class ActorManagerResource {
            @PostMapping(path = "/actor-roles/{itProfileRoleGUID}/it-profile-role-appointments/{itProfileGUID}/detach")
            public VoidResponse detachITProfileRoleFromProfile(@PathVariable String serverName,
                                                               @RequestBody (required = false)
                                                               DeleteRelationshipRequestBody requestBody) { return null; }
            @PostMapping(path = {"/actor-roles/{actorRoleGUID}/delete","/solution-roles/{actorRoleGUID}/delete"})
            public VoidResponse deleteActorRole(@RequestBody (required = false) DeleteElementRequestBody requestBody) { return null; }
            @PostMapping(path = "/assets/{guid}/endpoints/retrieve")
            public VoidResponse getEndpoints(@RequestBody ResultsRequestBody requestBody) { return null; }
        }
    """,
}


def _truth(tmp_path):
    impl = tmp_path / "open-metadata-implementation"
    for rel, src in FILES.items():
        f = impl / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(textwrap.dedent(src))
    return omvs_audit.load_java_truth(str(tmp_path))


def test_generic_url_marker_endpoints_resolve_for_any_service(tmp_path):
    java = _truth(tmp_path)
    assert java.lookup("POST", "/actor-manager/actor-roles/{}/it-profile-role-appointments/{}/detach") == {
        "DeleteRelationshipRequestBody"}
    # both paths of a multi-path mapping are indexed
    assert java.lookup("POST", "/actor-manager/solution-roles/{}/delete") == {"DeleteElementRequestBody"}
    assert java.lookup("POST", "/actor-manager/no-such/{}/thing") is None


def test_sibling_under_polymorphic_base_is_rejected_elsewhere_class_is_ignored(tmp_path):
    java = _truth(tmp_path)
    # the live 400 from ISSUE-163: DeleteElementRequestBody where DeleteRelationshipRequestBody is declared
    assert java.rejects("DeleteRelationshipRequestBody", "DeleteElementRequestBody")
    assert not java.rejects("DeleteRelationshipRequestBody", "DeleteRelationshipRequestBody")
    # ResultsRequestBody has no @JsonTypeInfo: "class" is ignored, so not a rejection
    assert not java.accepts("ResultsRequestBody", "FilterRequestBody")
    assert not java.rejects("ResultsRequestBody", "FilterRequestBody")


def test_known_classes_and_class_constant_scan(tmp_path):
    java = _truth(tmp_path)
    assert "PersonRoleAppointmentProperties" in java.known_classes
    py = tmp_path / "client.py"
    py.write_text('def f():\n    """Uses PersonAppointmentProperties."""\n'
                  '    return ["PersonAppointmentProperties"], {"class": "DeleteElementRequestBody"}\n')
    found = {name for _, name in omvs_audit.class_constants(str(py))}
    # docstring prose is not a bare class-name constant
    assert found == {"PersonAppointmentProperties", "DeleteElementRequestBody"}
    assert "PersonAppointmentProperties" not in java.known_classes


def test_inherited_json_fields_and_json_property_rename(tmp_path):
    impl = tmp_path / "open-metadata-implementation" / "frameworks" / "src" / "main" / "java" / "rest"
    impl.mkdir(parents=True)
    (impl / "BaseOptions.java").write_text(
        "public class BaseOptions extends Object {\n"
        "    private static final long serialVersionUID = 1L;\n"
        "    private boolean cascadedDelete = false;\n}\n")
    (impl / "ThingRequestBody.java").write_text(
        "public class ThingRequestBody extends BaseOptions {\n"
        "    @JsonProperty(\"class\")\n    private String className;\n"
        "    private List<String> anchorScopeGUIDs = null;\n}\n")
    java = omvs_audit.load_java_truth(str(tmp_path))
    # inherited field included, serialVersionUID and statics excluded, rename honoured
    assert java.json_fields("ThingRequestBody") == {"class", "anchorScopeGUIDs", "cascadedDelete"}
    assert java.json_fields("NoSuchRequestBody") is None


def test_helper_field_map_follows_local_aliases(tmp_path):
    src = tmp_path / "client.py"
    src.write_text(textwrap.dedent('''
        class C:
            async def _async_find_request(self, url, search_string="*", property_names=None):
                effective = None if search_string == "*" else search_string
                if property_names:
                    body = {"class": "FindPropertyNamesProperties", "propertyValue": search_string,
                            "propertyNames": property_names}
                else:
                    body = {"class": "SearchStringRequestBody", "searchString": effective}
    '''))
    params, mapping = omvs_audit.discover_helper_fields(str(src))["_async_find_request"]
    assert params == ["url", "search_string", "property_names"]
    # search_string reaches two keys (one via the `effective` local); a field is
    # only "dropped" when every key it can fill is dropped
    assert mapping["search_string"] == {"propertyValue", "searchString"}
    assert mapping["property_names"] == {"propertyNames"}


def test_client_drops_flags_keys_the_pyegeria_model_does_not_read(tmp_path):
    src = tmp_path / "client.py"
    src.write_text('def f(x):\n'
                   '    return {"class": "SearchStringRequestBody", "searchString": x,\n'
                   '            "zoneFilter": x, "relationshipPageSize": 5, "start_from": 0}\n')
    # zoneFilter / relationshipPageSize are near-misses of governanceZoneFilter /
    # relationshipsPageSize; start_from is a field name, accepted via populate_by_name
    assert omvs_audit.client_drops(str(src)) == [
        (2, "SearchStringRequestBody", ["relationshipPageSize", "zoneFilter"])]
