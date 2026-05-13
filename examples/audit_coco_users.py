
import json
from pathlib import Path
from pyegeria import load_app_config, EgeriaTech

load_app_config(env_file=str(Path(__file__).parent / ".env"))

user = "ivorpadlock"
password = "secret"
client = EgeriaTech(user_id=user, user_pwd=password)
token = client.create_egeria_bearer_token()


def extract_zone_membership_profile(element: dict) -> tuple[str, dict] | None:
    """Return (zone_display_name, classificationProperties) from a governance zone element, or None."""
    if not isinstance(element, dict):
        return None
    header = element.get("elementHeader", {})
    zone_profile = header.get("zoneMembershipProfile")
    if not zone_profile:
        return None
    cp = zone_profile.get("classificationProperties", {})
    if not cp:
        return None
    props = element.get("properties", element.get("governanceZoneProperties", {}))
    name = props.get("displayName") or props.get("qualifiedName") or header.get("guid", "unknown")
    return name, cp


def find_zone_membership_profiles(data) -> list[tuple[str, dict]]:
    """Collect (name, classificationProperties) for every zone element that has a membership profile."""
    items = data if isinstance(data, list) else [data]
    results = []
    for item in items:
        found = extract_zone_membership_profile(item)
        if found:
            results.append(found)
    return results


def make_zone_membership_summary_bar(cp: dict, zone_name: str) -> str:
    """Bar chart comparing total / anchored / all membership counts for a zone."""
    data = [
        {"scope": "Zone Direct",    "count": cp.get("totalMembership", 0)},
        {"scope": "Anchored Total", "count": cp.get("anchoredTotalMembership", 0)},
        {"scope": "All (inc. sub)", "count": cp.get("allTotalMembership", 0)},
    ]
    title = f"Zone Membership Summary — {zone_name}"
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": data},
        "mark": {"type": "bar", "tooltip": True},
        "encoding": {
            "x": {"field": "scope", "type": "nominal", "axis": {"labelAngle": -20}, "title": "Scope"},
            "y": {"field": "count", "type": "quantitative", "title": "Asset Count"},
            "color": {
                "field": "scope",
                "type": "nominal",
                "scale": {
                    "domain": ["Zone Direct", "Anchored Total", "All (inc. sub)"],
                    "range": ["#4c78a8", "#72b7b2", "#54a24b"]
                }
            },
            "tooltip": [
                {"field": "scope", "type": "nominal", "title": "Scope"},
                {"field": "count", "type": "quantitative", "title": "Count"}
            ]
        }
    }
    return json.dumps(spec, indent=2)


def make_zone_type_breakdown_bar(cp: dict, zone_name: str) -> str | None:
    """Horizontal bar chart for per-asset-type membership counts (typeMembership dict), or None if absent."""
    type_membership = cp.get("typeMembership")
    if not isinstance(type_membership, dict) or not type_membership:
        return None
    data = [{"assetType": k, "count": v} for k, v in type_membership.items() if v]
    if not data:
        return None
    title = f"Zone Asset Types — {zone_name}"
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": data},
        "mark": {"type": "bar", "tooltip": True},
        "encoding": {
            "y": {"field": "assetType", "type": "nominal", "sort": "-x", "title": "Asset Type"},
            "x": {"field": "count", "type": "quantitative", "title": "Count"},
            "color": {"field": "assetType", "type": "nominal", "legend": None},
            "tooltip": [
                {"field": "assetType", "type": "nominal", "title": "Type"},
                {"field": "count", "type": "quantitative", "title": "Count"}
            ]
        }
    }
    return json.dumps(spec, indent=2)


def make_zone_type_breakdown_pie(cp: dict, zone_name: str) -> str | None:
    """Donut pie chart for per-asset-type membership distribution, or None if absent."""
    type_membership = cp.get("typeMembership")
    if not isinstance(type_membership, dict) or not type_membership:
        return None
    data = [{"assetType": k, "count": v} for k, v in type_membership.items() if v]
    if not data:
        return None
    title = f"Zone Asset Type Mix — {zone_name}"
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": title,
        "description": title,
        "data": {"values": data},
        "mark": {"type": "arc", "innerRadius": 50, "tooltip": True},
        "encoding": {
            "theta": {"field": "count", "type": "quantitative"},
            "color": {"field": "assetType", "type": "nominal"},
            "tooltip": [
                {"field": "assetType", "type": "nominal", "title": "Type"},
                {"field": "count", "type": "quantitative", "title": "Count"}
            ]
        }
    }
    return json.dumps(spec, indent=2)


def print_zone_vega_charts(data):
    """Extract zone membership profiles from governance definition results and print vega-lite charts."""
    profiles = find_zone_membership_profiles(data)
    if not profiles:
        print("\n[No zoneMembershipProfile classificationProperties found in result]")
        return

    for zone_name, cp in profiles:
        total = cp.get("totalMembership", "?")
        print(f"\n## Zone Membership Charts — {zone_name}  (direct members: {total})\n")

        print("### Membership Scope Summary\n")
        print("```vega-lite")
        print(make_zone_membership_summary_bar(cp, zone_name))
        print("```\n")

        type_bar = make_zone_type_breakdown_bar(cp, zone_name)
        if type_bar:
            print("### Asset Type Breakdown (bar)\n")
            print("```vega-lite")
            print(type_bar)
            print("```\n")

        type_pie = make_zone_type_breakdown_pie(cp, zone_name)
        if type_pie:
            print("### Asset Type Mix (donut)\n")
            print("```vega-lite")
            print(type_pie)
            print("```\n")


# coco_user_dir = client.find_assets(search_string='cocoUserDirectory',
#                                    metadata_element_type="SecretsCollection",
#                                    report_spec = 'Secrets-Collection-User-Profile-Charts',
#                                    output_format = 'REPORT')
# print(f"cocoUserDirectory: {json.dumps(coco_user_dir, indent=2)}")
# print(coco_user_dir)
# identities = client.find_user_identities()
# print(f"identities: {json.dumps(identities, indent=2)}")

# zones = client.find_governance_definitions(search_string="*", metadata_element_type="GovernanceZone")
# print(f"zones: {json.dumps(zones, indent=2)}")

digital_products_zone = client.find_governance_definitions(search_string="digital-products",
                                                           metadata_element_type="GovernanceZone",
                                                           report_spec="Governance-Zone-Overview-Charts",
                                                           output_format="JSON")
print(f"digital-products: {json.dumps(digital_products_zone, indent=2)}")

# print_zone_vega_charts(digital_products_zone)