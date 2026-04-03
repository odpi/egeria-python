import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.parsing import AttributeFirstParser


@pytest.mark.asyncio
async def test_parser_unknown_label_suggests_closest_canonical_name():
    cmd = DrECommand(
        verb="Link",
        object_type="Agreement T&C",
        attributes={
            "Agreement Name": "Agreement::SalesForecast::Finance::DataSharing::1.0",
            "Terms and Conditions Id": "TermsAndConditions::SalesForecast::DataSharing::1.0",
        },
        raw_block="# Link Agreement T&C",
    )

    result = await AttributeFirstParser(cmd, directive="process").parse()

    assert any("Unknown attribute label" in warning for warning in result["warnings"])
    assert any("Terms & Conditions Id" in warning for warning in result["warnings"])


@pytest.mark.asyncio
async def test_parser_missing_required_attribute_includes_provided_labels_context():
    cmd = DrECommand(
        verb="Link",
        object_type="Agreement T&C",
        attributes={
            "Agreement Name": "Agreement::SalesForecast::Finance::DataSharing::1.0",
            "Terms and Conditions Id": "TermsAndConditions::SalesForecast::DataSharing::1.0",
        },
        raw_block="# Link Agreement T&C",
    )

    result = await AttributeFirstParser(cmd, directive="process").parse()

    missing_errors = [e for e in result["errors"] if "Missing required attribute: 'Terms & Conditions Id'" in e]
    assert missing_errors
    assert "Provided attributes:" in missing_errors[0]
    assert "Terms and Conditions Id" in missing_errors[0]


