from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body, update_gov_body_for_type


def test_set_gov_prop_body_includes_notification_type_custom_fields():
    attrs = {
        "Display Name": {"value": "CRM Data Quality Breach Alert"},
        "Summary": {"value": "Notification summary"},
        "Description": {"value": "Notification description"},
        "Domain Identifier": {"value": "DATA"},
        "Planned Start Date": {"value": "2026-01-01"},
        "Planned Completion Date": {"value": "2026-12-31"},
        "Multiple Notifications Permitted": {"value": True},
        "Notification Interval": {"value": "86400000"},
        "Minimum Notification Interval": {"value": "3600000"},
        "Next Scheduled Notification": {"value": "2026-04-01T07:00:00Z"},
        "Notification Count": {"value": "0"},
    }

    body = set_gov_prop_body(
        "Notification Type",
        "NotificationType::SalesForecast::CRMDataQualityBreachAlert::1.0",
        attrs,
    )

    assert body["class"] == "NotificationTypeProperties"
    assert body["domainIdentifier"] == 1
    assert body["plannedStartDate"] == "2026-01-01"
    assert body["plannedCompletionDate"] == "2026-12-31"
    assert body["multipleNotificationsPermitted"] is True
    assert body["notificationInterval"] == "86400000"
    assert body["minimumNotificationInterval"] == "3600000"
    assert body["nextScheduledNotification"] == "2026-04-01T07:00:00Z"
    assert body["notificationCount"] == "0"


def test_update_gov_body_for_type_unhandled_type_keeps_base_body():
    base = {"class": "SomeNewGovernanceTypeProperties", "displayName": "X"}
    out = update_gov_body_for_type("Some New Governance Type", dict(base), {})
    assert out == base


