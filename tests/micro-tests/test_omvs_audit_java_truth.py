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
