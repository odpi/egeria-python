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
        "Minimum Notification Interval": {"value": "60"},
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
    assert body["minimumNotificationInterval"] == "60"
    assert body["notificationCount"] == "0"


def test_set_gov_prop_body_notification_type_never_sends_removed_or_informational_fields():
    # Egeria 6.3 removed notificationInterval (deprecated in 6.2, ignored if sent), and
    # nextScheduledNotification is informational only -- maintained by the notification manager.
    # A document that still carries the old attributes must not send either.
    attrs = {
        "Display Name": {"value": "Old style"},
        "Notification Interval": {"value": "86400000"},
        "Next Scheduled Notification": {"value": "2026-04-01T07:00:00Z"},
        "Minimum Notification Interval": {"value": "10"},
    }
    body = set_gov_prop_body("Notification Type", "NotificationType::OldStyle", attrs)
    assert "notificationInterval" not in body
    assert "nextScheduledNotification" not in body
    assert body["minimumNotificationInterval"] == "10"


def test_update_gov_body_for_type_unhandled_type_keeps_base_body():
    base = {"class": "SomeNewGovernanceTypeProperties", "displayName": "X"}
    out = update_gov_body_for_type("Some New Governance Type", dict(base), {})
    assert out == base


