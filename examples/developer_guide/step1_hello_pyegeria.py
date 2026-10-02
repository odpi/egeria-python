"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Developer Guide step 1: connect to Egeria with pyegeria and list the glossaries. No Textual yet.

   Run:  python examples/developer_guide/step1_hello_pyegeria.py
"""

from pyegeria import PyegeriaException, print_basic_exception

from common import connection_settings, fetch_glossaries


def main() -> None:
    conn = connection_settings()
    print(f"Connecting to {conn.view_server} at {conn.platform_url} as {conn.user_name}")
    try:
        glossaries = fetch_glossaries(conn)
    except PyegeriaException as e:
        print_basic_exception(e)
        return

    if not glossaries:
        print("No glossaries found")
        return
    for glossary in glossaries:
        print(f"{glossary['Display Name']:<55} {glossary['GUID']}")


if __name__ == "__main__":
    main()
