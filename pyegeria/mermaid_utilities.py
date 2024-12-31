"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module provides a set of utility functions to render Mermaid markdown in a Jupyter notebook.

A running Egeria environment is needed to run these functions.
These functions have been tested in a Jupyter notebook - but may work in other environments.

"""

import os
import time

import nest_asyncio

nest_asyncio.apply()
from pyegeria import (
    AutomatedCuration,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from IPython.display import display, HTML
from rich.console import Console

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def load_mermaid():
    """Inject Mermaid.js library"""
    mermaid_js = """
    <script type="text/javascript">
        if (!window.mermaid) {
            var mermaidScript = document.createElement('script');
            mermaidScript.src = "https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js";
            document.head.appendChild(mermaidScript);
        }
    </script>
    """
    display(HTML(mermaid_js))


def render_mermaid(mermaid_code):
    """Function to display a Mermaid diagram in a Jupyter notebook"""
    mermaid_html = f"""
    <div class="mermaid">
        {mermaid_code}
    </div>
    <script type="text/javascript">
        if (window.mermaid) {{
    mermaid.initialize({{startOnLoad: true}});
    mermaid.contentLoaded();
    }}
    </script>
    """
    display(HTML(mermaid_html))


def generate_process_graph(
    process_guid: str,
    view_server: str = EGERIA_VIEW_SERVER,
    url: str = EGERIA_VIEW_SERVER_URL,
    user_id: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
) -> str:
    """Generate Mermaid Markdown text reflecting the Egeria process graph identified by the GUID

    Parameters
        ----------
        process_guid: str
            The identity of the progress to generate a graph of.

        Returns
        -------
        str

        A Mermaid markdown string

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

    """
    console = Console()
    a_client = AutomatedCuration(view_server, url, user_id, user_pass)
    token = a_client.create_egeria_bearer_token()
    try:
        start_time = time.perf_counter()
        response = a_client.get_gov_action_process_graph(process_guid)
        duration = time.perf_counter() - start_time

        if type(response) is dict:
            process_steps: [dict]
            step_links: [dict] = []
            gov_process_qn = response["governanceActionProcess"]["processProperties"][
                "qualifiedName"
            ]
            gov_process_dn = response["governanceActionProcess"]["processProperties"][
                "displayName"
            ]

            md = f"\n---\ntitle: {gov_process_dn}\n---\nflowchart LR\n"
            header = '%%{init: {"flowchart": {"htmlLabels": false}} }%%\n'
            md += header
            element = response["firstProcessStep"]["element"]
            qname = element["processStepProperties"]["qualifiedName"]
            dname = element["processStepProperties"]["displayName"]
            domain_id = element["processStepProperties"]["domainIdentifier"]
            guid = element["elementHeader"]["guid"]
            wait = element["processStepProperties"]["waitTime"]
            ignore_mult_trig = element["processStepProperties"][
                "ignoreMultipleTriggers"
            ]
            link = response["firstProcessStep"]["linkGUID"]

            md = f'{md}\nStep1("`**{dname}**\n*nwait_time*: {wait}\n*nmult_trig*: {ignore_mult_trig}`")'
            process_steps = {
                qname: {
                    "step": "Step1",
                    "displayName": dname,
                    "guid": guid,
                    "domain": domain_id,
                    "ignoreMultTrig": ignore_mult_trig,
                    "waitTime": wait,
                    "link_guid": link,
                }
            }
            next_steps = response.get("nextProcessSteps", None)
            if next_steps is not None:
                i = 1
                for step in next_steps:
                    i += 1
                    qname = step["processStepProperties"]["qualifiedName"]
                    dname = step["processStepProperties"]["displayName"]
                    wait = step["processStepProperties"]["waitTime"]
                    step = f"Step{i}"
                    md = f'{md}\n{step}("`**{dname}**\n*wait_time*: {wait}\n*mult_trig*: {ignore_mult_trig}`")'
                    process_steps.update(
                        {
                            qname: {
                                "step": step,
                                "displayName": dname,
                                "guid": guid,
                                "domain": domain_id,
                                "ignoreMultTrig": ignore_mult_trig,
                                "waitTime": wait,
                            }
                        }
                    )  # process_steps.append({qname: {"step": step,"displayName": dname, "waitTime": wait}})
            # print(md)
            # Now process the links
            process_step_links = response.get("processStepLinks", None)
            if process_step_links is not None:
                for slink in process_step_links:
                    prev_step_name = slink["previousProcessStep"]["uniqueName"]
                    next_step_name = slink["nextProcessStep"]["uniqueName"]
                    next_step_link_guid = slink["nextProcessStepLinkGUID"]
                    guard = slink["guard"]
                    mandatory_guard = slink["mandatoryGuard"]
                    # print(f"\n\n Links: prev_step: {prev_step_name}\t next_step: {next_step_name}\t next_step_link:
                    # {next_step_link_guid}\t Guard: {guard}\t mandatory_guard: {mandatory_guard}")
                    step_links.append(
                        {
                            next_step_link_guid: {
                                "prev_step_name": prev_step_name,
                                "next_step_name": next_step_name,
                                "guard": guard,
                                "mandatory_guard": mandatory_guard,
                            }
                        }
                    )
                    step_p = process_steps[prev_step_name]["step"]
                    step_n = process_steps[next_step_name]["step"]
                    if mandatory_guard:
                        link = f"Mandatory:{guard}"
                    else:
                        link = guard
                    md = f"{md}\n{step_p}-->|{link}|{step_n}"
                i = 1

            return md

        elif type(response) is str:
            console.log("\n\n" + response)
        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"

    finally:
        a_client.close_session()
