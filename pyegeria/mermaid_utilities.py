"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module provides a set of utility functions to render Mermaid markdown in a Jupyter notebook.

A running Egeria environment is needed to run these functions.
These functions have been tested in a Jupyter notebook - but may work in other environments.

"""
import html
import os
import time
import uuid

import nest_asyncio

nest_asyncio.apply()
from IPython.display import HTML, display
from rich.console import Console

from pyegeria.automated_curation_omvs import AutomatedCuration
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from pyegeria._globals import NO_ELEMENTS_FOUND

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
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
EGERIA_MERMAID_FOLDER = os.environ.get("EGERIA_MERMAID_FOLDER", "./work/mermaid_graphs")


def load_mermaid():
    """Inject Mermaid.js library"""
    # Alternative CDN URL via unpkg
    mermaid_js = """
    <script src="https://unpkg.com/mermaid@11.4.1/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            mermaid.initialize({startOnLoad: true});
        });
    </script>

    """

    display(HTML(mermaid_js))


def render_mermaid(mermaid_code):
    return display(HTML(construct_mermaid_html(mermaid_code)))


def parse_mermaid_code(mermaid_code):
    parts = mermaid_code.split("---", maxsplit=3)
    if len(parts) == 3:
        full_title = parts[1].strip()
        title_l = full_title.split("[")[0]
        title = title_l.replace("title: ", "")
        guid = full_title.split("[")[1].split("]")[0]
        guid = " " if guid is None else guid
        mermaid_code = parts[2].strip()
    else:
        title = "Unlabeled diagram"
        guid = " "
    return title, guid, mermaid_code


def old_construct_mermaid_html(mermaid_str: str) -> str:
    """Function to display a HTML code in a Jupyter notebook"""
    title_label, guid, mermaid_code = parse_mermaid_code(mermaid_str)

    html_section1 = """
    <!DOCTYPE html>
    <html>
        <head>
          <style type="text/css">
            #mySvgId {
            width: 100%;
            height: 600px;
            overflow: scroll;
            border: 2px solid #ccc;
            position: relative;
            margin-bottom: 10px;
            }
            svg {
            cursor: grab;
            }
    
          </style>
        </head>
    """
    html_section2 = f"""
        <title>{title_label}</title>
        <h3>{title_label}</h3>
        GUID : {guid}

    """
    html_section3 = """
        <body>
        
          <div id="graphDiv"></div>
          <script src="https://bumbu.me/svg-pan-zoom/dist/svg-pan-zoom.min.js"></script>
          <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    
            mermaid.initialize({startOnLoad: false});
            await mermaid.run({
              querySelector: '.mermaid',
              postRenderCallback: (id) => {
                const container = document.getElementById("diagram-container");
                const svgElement = container.querySelector("svg");
    
                // Initialize Panzoom
                const panzoomInstance = Panzoom(svgElement, {
                  maxScale: 5,
                  minScale: 0.5,
                  step: 0.1,
                });
    
                // Add mouse wheel zoom
                container.addEventListener("wheel", (event) => {
                  panzoomInstance.zoomWithWheel(event);
                });
              }
            });
    
    
            const drawDiagram = async function () {
              const element = document.querySelector('#graphDiv');
             const graphDefinition = `
    """

    html_section4 = r"""`;
              const {svg} = await mermaid.render('mySvgId', graphDefinition);
              element.innerHTML = svg.replace(/( )*max-width:( 0-9\.)*px;/i, '');
    
              var doPan = false;
              var eventsHandler;
              var panZoom;
              var mousepos;
    
              eventsHandler = {
                haltEventListeners: ['mousedown', 'mousemove', 'mouseup']
    
                , mouseDownHandler: function (ev) {
                  if (event.target.className == "[object SVGAnimatedString]") {
                    doPan = true;
                    mousepos = {x: ev.clientX, y: ev.clientY}
                  }
                  ;
                }
    
                , mouseMoveHandler: function (ev) {
                  if (doPan) {
                    panZoom.panBy({x: ev.clientX - mousepos.x, y: ev.clientY - mousepos.y});
                    mousepos = {x: ev.clientX, y: ev.clientY};
                    window.getSelection().removeAllRanges();
                  }
                }
    
                , mouseUpHandler: function (ev) {
                  doPan = false;
                }
    
                , init: function (options) {
                  options.svgElement.addEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.addEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.addEventListener('mouseup', this.mouseUpHandler, false);
                }
    
                , destroy: function (options) {
                  options.svgElement.removeEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.removeEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.removeEventListener('mouseup', this.mouseUpHandler, false);
                }
              }
              panZoom = svgPanZoom('#mySvgId', {
                zoomEnabled: true
                , controlIconsEnabled: true
                , fit: 1
                , center: 1
                , customEventsHandler: eventsHandler
              })
            };
            await drawDiagram();
          </script>
        </body>    
    """

    return html_section1 + html_section2 + html_section3 + mermaid_code + html_section4


def construct_mermaid_html(mermaid_str: str) -> str:
    """Function to display a HTML code in a Jupyter notebook

    Constructs HTML for a single Mermaid graph with pan and zoom support.
    Each call overwrites the previous graph.

    :param mermaid_code: The Mermaid code for the graph.
    :param graph_id: An optional unique graph ID (default is 'mermaid-graph').
    :return: The HTML content for the Mermaid graph with pan and zoom enabled.

    """
    title_label, guid, mermaid_code = parse_mermaid_code(mermaid_str)

    graph_id = f"mermaid-graph-{guid}"
    escaped_header = html.escape(title_label) if title_label else ""  # Sanitize the header safely
    escaped_mermaid_code = html.escape(mermaid_code)

    header_html = f"""
        <h3 id="{graph_id}-heading" style="margin: 20px 0; font-size: 1.5em; text-align: center;">
            {escaped_header}
        </h3>
        <p id="{graph_id}-subheading" style="margin: 0; padding: 5px; font-size: 1em; text-align: center; color: gray; flex: 0 0 auto;">
            GUID: {guid}
        </p>
        """ if title_label else ""

    html_content = f"""
    <div id="{graph_id}-wrapper" style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: stretch;">
        
        <!-- Title/Heading -->
        
        {header_html if header_html else ""}
        <!-- Mermaid Diagram -->
        <div id="{graph_id}-container" class="diagram-container"
             style="width: 100%; flex: 1 1 auto; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden;">
            <div id="{graph_id}" class="mermaid"
                 style="width: 100%; height: 100%; cursor: grab; user-select: none; margin: 0; padding: 0;">
                {escaped_mermaid_code}
            </div>
        </div>
    </div>
    
    <style>
        /* Ensure no margins or padding for the body or html in Jupyter */
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }}
        /* General reset for Jupyter Notebook's extra spacing */
        #notebook, .container, .cell, .output_area {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        .diagram-container {{
            width: 100%;
            height: 100%;
            overflow: hidden; /* Prevent scrollbars during zoom/pan */
        }}
        h2 {{
            margin: 0;
            padding: 10px;
            font-size: 24px;
            text-align: center;
            flex: 0 0 auto; /* Fix height explicitly for heading */
        }}
        .mermaid {{
            margin: 0;
            padding: 0;
        }}
    </style>
    
    <script>
        (function() {{
            const graphId = "{graph_id}";  // Pass the graph ID

            function loadScript(url, callback) {{
                const script = document.createElement('script');
                script.src = url;
                script.onload = callback;
                document.head.appendChild(script);
            }}
            
            // Initialize Mermaid and render the diagram
            function initializeMermaid() {{
                mermaid.initialize({{startOnLoad: false}});
                mermaid.init(undefined, "#" + graphId);

                setTimeout(() => {{
                    const container = document.getElementById(graphId);
                    if (!container) {{
                        console.error("Container not found for graph:", graphId);
                        return;
                    }}

                    const svg = container.querySelector("svg");
                    if (!svg) {{
                        console.error("SVG not rendered by Mermaid.");
                        return;
                    }}

                    console.log("SVG rendered. Applying pan & zoom.");

                    // Adjust to container size
                    const containerElement = document.getElementById("{graph_id}-container");
                    svg.setAttribute("width", containerElement.offsetWidth);
                    svg.setAttribute("height", containerElement.offsetHeight);

                    // Add pan/zoom functionality
                    loadScript("https://cdn.jsdelivr.net/npm/svg-pan-zoom/dist/svg-pan-zoom.min.js", () => {{
                        const panZoom = svgPanZoom(svg, {{
                            zoomEnabled: true,
                            controlIconsEnabled: true,
                            fit: true,
                            center: true,
                            minZoom: 0.5,
                            maxZoom: 10
                        }});

                        // Reinitialize pan-zoom on window resize
                        function onResize() {{
                            panZoom.resize();
                            panZoom.fit();
                            panZoom.center();
                        }}
                        window.addEventListener('resize', onResize);

                        console.log("Pan & zoom initialized successfully.");
                    }});
                }}, 500);
            }}

            // Load Mermaid.js and initialize
            if (typeof mermaid === "undefined") {{
                loadScript("https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js", initializeMermaid);
            }} else {{
                initializeMermaid();
            }}
        }})();
    </script>

    """


    return html_content
    # mermaid_html = f"""
    #     <h2 style="text-align: center; color: #007acc; margin-bottom: 16px;">
    #         {escaped_header}
    #     </h2>
#         """ if header else ""
# #     <div class="diagram-container" style="width: 90%; max-width: 800px; margin: auto; padding: 20px; background: white; border: 1px solid #ddd; border-radius: 12px; position: relative;">
# #         {header_html}
# #         <div class="pan-zoom-container" style="width: 100%; height: 500px; overflow: hidden; position: relative; background: #f9f9f9; border: 1px solid #ccc; cursor: grab;">
# #             <div id="{graph_id}" class="mermaid pan-zoom-content" style="position: absolute; transform-origin: 0 0; cursor: grab;">
# #                 {escaped_mermaid_code}
# #             </div>
# #         </div>
# #     </div>
# #     <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
# #     <script>
# #         // Initialize Mermaid.js and set up pan/zoom
# #         mermaid.initialize({{ startOnLoad: true }});
# #
# #         const container = document.querySelector('.pan-zoom-container');
# #         const content = document.querySelector('.pan-zoom-content');
# #         const rect = content.getBoundingClientRect();
# #
# #         let scale = 1; // Current zoom level
# #         let panX = 0;  // X-axis pan offset
# #         let panY = 0;  // Y-axis pan offset
# #         let isDragging = false;
# #         let startX, startY;
# #
# #         // Helper: Apply transformations
# #         const applyTransform = () => {{
# #             content.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{scale}})`;
# #         }};
# #
# #         // Helper: Center the diagram and fit it to the container
# #         const centerAndFitDiagram = () => {{
# #             const containerRect = container.getBoundingClientRect();
# #             const rect = content.getBoundingClientRect();
# #
# #             scale = Math.min(
# #                 containerRect.width / rect.width,
# #                 containerRect.height / rect.height
# #             );
# #
# #             panX = (containerRect.width - rect.width * scale) / 2;
# #             panY = (containerRect.height - rect.height * scale) / 2;
# #
# #             applyTransform();
# #             console.log("Diagram centered and fitted.");
# #         }};
# #
# #         // Add zoom functionality
# #         container.addEventListener('wheel', function(event) {{
# #             event.preventDefault();
# #             const zoomSpeed = 0.1;
# #             const previousScale = scale;
# #
# #             if (event.deltaY < 0) {{
# #                 scale = Math.min(scale + zoomSpeed, 4);
# #             }} else {{
# #                 scale = Math.max(scale - zoomSpeed, 0.5);
# #             }}
# #
# #             const zoomRatio = scale / previousScale;
# #             panX -= (event.clientX - container.getBoundingClientRect().left) * (zoomRatio - 1);
# #             panY -= (event.clientY - container.getBoundingClientRect().top) * (zoomRatio - 1);
# #
# #             applyTransform();
# #         }});
# #
# #         // Add drag functionality for panning
# #         container.addEventListener('mousedown', function(event) {{
# #             isDragging = true;
# #             startX = event.clientX - panX;
# #             startY = event.clientY - panY;
# #             container.style.cursor = "grabbing";
# #         }});
# #
# #         container.addEventListener('mousemove', function(event) {{
# #             if (!isDragging) return;
# #
# #             panX = event.clientX - startX;
# #             panY = event.clientY - startY;
# #
# #             applyTransform();
# #         }});
# #
# #         container.addEventListener('mouseup', function() {{
# #             isDragging = false;
# #             container.style.cursor = "grab";
# #         }});
# #
# #         container.addEventListener('mouseleave', function() {{
# #             isDragging = false;
# #             container.style.cursor = "grab";
# #         }});
# #
# #         // Center diagram after rendering by Mermaid
# #         setTimeout(centerAndFitDiagram, 200);
# #     </script>
# # """
#
#     return mermaid_html



def save_mermaid_html(
    title: str, mermaid_str: str, folder: str = EGERIA_MERMAID_FOLDER
):
    """Save a Mermaid diagram to a file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    mermaid_file = os.path.join(folder, title + ".html")

    payload = construct_mermaid_html(mermaid_str)

    with open(mermaid_file, "w") as f:
        f.write(payload)
    return mermaid_file


def save_mermaid_graph(title, mermaid_str, folder: str = EGERIA_MERMAID_FOLDER):
    """Save a Mermaid diagram to a file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    mermaid_file = os.path.join(folder, title + ".html")

    title, mermaid_code = parse_mermaid_code(mermaid_str)

    html_prefix = """
    <html>
        <head>
          <style type="text/css">
            #mySvgId {
            width: 100%;
            height: 100%;
            overflow: hidden;
            border: 1px solid #ccc;
            position: relative;
            margin-bottom: 10px;
            }
            svg {
            cursor: grab;
            }
        
          </style>
        </head>
        
        <body>
          <div id="graphDiv"></div>
          <script src="https://bumbu.me/svg-pan-zoom/dist/svg-pan-zoom.min.js"></script>
          <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        
            mermaid.initialize({startOnLoad: false});
            await mermaid.run({
              querySelector: '.mermaid',
              postRenderCallback: (id) => {
                const container = document.getElementById("diagram-container");
                const svgElement = container.querySelector("svg");
        
                // Initialize Panzoom
                const panzoomInstance = Panzoom(svgElement, {
                  maxScale: 5,
                  minScale: 0.5,
                  step: 0.1,
                });
        
                // Add mouse wheel zoom
                container.addEventListener("wheel", (event) => {
                  panzoomInstance.zoomWithWheel(event);
                });
              }
            });
        
        
            const drawDiagram = async function () {
              const element = document.querySelector('#graphDiv');
              const graphDefinition = `
    """

    html_postfix = r"""`;
              const {svg} = await mermaid.render('mySvgId', graphDefinition);
              element.innerHTML = svg.replace(/( )*max-width:( 0-9\.)*px;/i, '');
        
              var doPan = false;
              var eventsHandler;
              var panZoom;
              var mousepos;
        
              eventsHandler = {
                haltEventListeners: ['mousedown', 'mousemove', 'mouseup']
        
                , mouseDownHandler: function (ev) {
                  if (event.target.className == "[object SVGAnimatedString]") {
                    doPan = true;
                    mousepos = {x: ev.clientX, y: ev.clientY}
                  }
                  ;
                }
        
                , mouseMoveHandler: function (ev) {
                  if (doPan) {
                    panZoom.panBy({x: ev.clientX - mousepos.x, y: ev.clientY - mousepos.y});
                    mousepos = {x: ev.clientX, y: ev.clientY};
                    window.getSelection().removeAllRanges();
                  }
                }
        
                , mouseUpHandler: function (ev) {
                  doPan = false;
                }
        
                , init: function (options) {
                  options.svgElement.addEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.addEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.addEventListener('mouseup', this.mouseUpHandler, false);
                }
        
                , destroy: function (options) {
                  options.svgElement.removeEventListener('mousedown', this.mouseDownHandler, false);
                  options.svgElement.removeEventListener('mousemove', this.mouseMoveHandler, false);
                  options.svgElement.removeEventListener('mouseup', this.mouseUpHandler, false);
                }
              }
              panZoom = svgPanZoom('#mySvgId', {
                zoomEnabled: true
                , controlIconsEnabled: true
                , fit: 1
                , center: 1
                , customEventsHandler: eventsHandler
              })
            };
            await drawDiagram();
          </script>
        </body>    
    """

    payload = html_prefix + mermaid_code + html_postfix

    with open(mermaid_file, "w") as f:
        f.write(payload)
    return mermaid_file


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
