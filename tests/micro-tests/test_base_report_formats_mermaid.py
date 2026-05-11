from pyegeria.view.base_report_formats import select_report_format


def test_collection_mindmap_report_spec_resolves_report():
    report_spec = select_report_format("Collection-MindMap", "REPORT")

    assert report_spec is not None
    assert report_spec["heading"] == "Collection Mind Map"
    assert report_spec["formats"]["types"] == ["REPORT"]


def test_collection_mindmap_report_spec_resolves_mermaid():
    report_spec = select_report_format("Collection-MindMap", "MERMAID")

    assert report_spec is not None
    assert report_spec["heading"] == "Collection Mind Map"
    assert report_spec["formats"]["types"] == ["MERMAID"]
    assert report_spec["formats"]["attributes"][0]["key"] == "collectionMermaidMindMap"