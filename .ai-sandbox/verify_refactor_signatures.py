
import inspect
import sys
from pyegeria.omvs.runtime_manager import RuntimeManager

def verify_signatures():
    methods_to_check = [
        # Cohorts
        "connect_to_cohort", "disconnect_from_cohort", "unregister_from_cohort",
        # Governance
        "refresh_gov_eng_config",
        # Integration Connectors
        "get_integ_connector_config_properties", "update_connector_configuration",
        "update_endpoint_address", "refresh_integration_connectors",
        "restart_integration_connectors", "refresh_integ_group_config",
        # Open Lineage & Archive
        "publish_open_lineage_event", "add_archive_content", "add_archive_file",
        # Server Admin
        "shutdown_and_unregister_server", "activate_server_with_stored_config", "shutdown_server",
        # Get/Find
        "get_platforms_by_name", "get_platforms_by_type", "get_platform_report",
        "get_servers_by_name", "get_server_report", "get_platform_by_guid",
        "get_server_by_guid", "get_platform_templates_by_type",
        "get_server_templates_by_dep_impl_type",
        # Async versions
        "_async_connect_to_cohort", "_async_disconnect_from_cohort", "_async_unregister_from_cohort",
        "_async_refresh_gov_eng_config", "_async_get_integ_connector_config_properties",
        "_async_update_connector_configuration", "_async_update_endpoint_address",
        "_async_refresh_integration_connectors", "_async_restart_integration_connectors",
        "_async_refresh_integ_group_config", "_async_publish_open_lineage_event",
        "_async_add_archive_content", "_async_add_archive_file", "_async_shutdown_and_unregister_server",
        "_async_activate_server_with_stored_config", "_async_shutdown_server",
        "_async_get_platforms_by_name", "_async_get_platforms_by_type", "_async_get_platform_report",
        "_async_get_servers_by_name", "_async_get_server_report", "_async_get_platform_by_guid",
        "_async_get_server_by_guid", "_async_get_platform_templates_by_type",
        "_async_get_server_templates_by_dep_impl_type"
    ]

    failed = False
    print("Verifying RuntimeManager signatures...")
    
    for method_name in methods_to_check:
        if not hasattr(RuntimeManager, method_name):
            print(f"FAILED: Method {method_name} not found in RuntimeManager")
            failed = True
            continue
            
        method = getattr(RuntimeManager, method_name)
        sig = inspect.signature(method)
        params = sig.parameters
        
        if "body" not in params:
            print(f"FAILED: Method {method_name} missing 'body' parameter")
            failed = True
        else:
            default_val = params["body"].default
            if default_val is not None: 
                # inspect.Parameter.empty is usually the value if no default, 
                # but here we typed it as Optional[dict] = None. 
                # So default should be None.
                if default_val != None: 
                     pass # None is expected. Optional warning if default is wrong?
            # print(f"PASS: {method_name}") 

    if failed:
        print("\nVerification FAILED.")
        sys.exit(1)
    else:
        print("\nVerification PASSED: All checked methods have 'body' parameter.")
        sys.exit(0)

if __name__ == "__main__":
    verify_signatures()
