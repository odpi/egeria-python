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
    title_label, guid, mermaid_code = parse_mermaid_code(mermaid_code)
    graph_id = f"mermaid-graph-{guid}-{str(uuid.uuid4())[:4]}"
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

    mermaid_html = f"""
    <div>{header_html}</div>
    <div class="mermaid">
        {escaped_mermaid_code}
    </div>
    <script type="text/javascript">
        if (window.mermaid) {{
    mermaid.initialize({{startOnLoad: true}});
    mermaid.contentLoaded();
    }}
    </script>
    """
    display(HTML(mermaid_html))


def render_mermaid_adv(mermaid_code):
    return display(HTML(construct_mermaid_web(mermaid_code)),)

def parse_mermaid_code(mermaid_code):
    parts = mermaid_code.split("---", maxsplit=3)
    guid = None
    if len(parts) == 3:
        full_title = parts[1].strip()
        if "[" in full_title:
            title_l = full_title.split("[")[0]
            title = title_l.replace("title: ", "")
            guid = full_title.split("[")[1].split("]")[0]
        else:
            title = full_title.replace("title: ", "")
        mermaid_code = parts[2].strip()
    else:
        title = None
    if guid is None:
        guid = str(uuid.uuid4())[:8]
    return title, guid, mermaid_code


def construct_mermaid_web(mermaid_str: str) -> str:
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

def construct_mermaid_jup(mermaid_str: str) -> str:
    """Function to display a HTML code in a Jupyter notebook

    Constructs HTML for a single Mermaid graph with pan and zoom support.
    Each call overwrites the previous graph.

    :param mermaid_code: The Mermaid code for the graph.
    :param graph_id: An optional unique graph ID (default is 'mermaid-graph').
    :return: The HTML content for the Mermaid graph with pan and zoom enabled.

    """
    title_label, guid, mermaid_code = parse_mermaid_code(mermaid_str)

    graph_id = f"mermaid-graph-{guid}-{str(uuid.uuid4())[:4]}"
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
            <style>
        /* Style for the diagram container */
        .diagram-container {{
            position: relative;
            width: 100%; /* Adjust the diagram container width */
            height: 500px; /* Set a fixed height for the container */
            margin: 0 auto;
            border: 1px solid #ccc; /* Optional border for visualization */
            overflow: hidden; /* Prevent content overflow outside the container */
        }}

        /* Style for zoom controls */
        .svg-pan-zoom_controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .svg-pan-zoom_controls button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
        }}
        .svg-pan-zoom_controls button:hover {{
            background-color: #0056b3;
        }}
    </style>

    <div id="{graph_id}-container" class="diagram-container">
        <!-- Mermaid diagram will be dynamically rendered here -->
        {header_html}
        <div id="{graph_id}" class="mermaid">
            {escaped_mermaid_code}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", () => {{
                // Initialize Mermaid and Pan-Zoom functionality
                const graph_id = "{graph_id}";

                function initializeMermaid(graph_id) {{
                    const containerElement = document.getElementById(`${{graph_id}}-container`);

                    if (!containerElement) {{
                        console.error(`Container with ID "${{graph_id}}-container" not found.`);
                        return;
                    }}

                    // Configure Mermaid
                    mermaid.initialize({{ startOnLoad: false, logLevel: "debug" }});
                    mermaid.init(undefined, `#${{graph_id}}`);

                    setTimeout(() => {{
                        const svg = containerElement.querySelector("svg");
                        if (!svg) {{
                            console.error(`SVG not rendered for ID "${{graph_id}}".`);
                            return;
                        }}

                        // Set initial size
                        svg.setAttribute("width", "100%");
                        svg.setAttribute("height", "100%");

                        // Initialize Pan-Zoom
                        const panZoom = svgPanZoom(svg, {{
                            zoomEnabled: true,
                            controlIconsEnabled: false,
                            fit: true,
                            center: true,
                            minZoom: 0.5,
                            maxZoom: 10,
                            contain: true
                        }});

                        // Add custom controls
                        const controlsContainer = document.createElement("div");
                        controlsContainer.className = "svg-pan-zoom_controls";
                        controlsContainer.innerHTML = `
                            <button id="${{graph_id}}-zoom-in">+</button>
                            <button id="${{graph_id}}-zoom-out">-</button>
                            <button id="${{graph_id}}-reset">Reset</button>
                        `;
                        containerElement.appendChild(controlsContainer);

                        // Handle controls
                        document.getElementById(`${{graph_id}}-zoom-in`).addEventListener("click", () => panZoom.zoomIn());
                        document.getElementById(`${{graph_id}}-zoom-out`).addEventListener("click", () => panZoom.zoomOut());
                        document.getElementById(`${{graph_id}}-reset`).addEventListener("click", () => {{
                            panZoom.resetZoom();
                            panZoom.center();
                        }});
                    }}, 500);
                }}

                if (typeof mermaid === "undefined") {{
                    const script = document.createElement('script');
                    script.src = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js";
                    script.onload = () => initializeMermaid(graph_id);
                    document.head.appendChild(script);
                }} else {{
                    initializeMermaid(graph_id);
                }}
            }});
        </script>

    """
    return html_content




def not_working_construct_mermaid_html(mermaid_str: str) -> str:
    """Function to display a HTML code in a Jupyter notebook

    Constructs HTML for a single Mermaid graph with pan and zoom support.
    Each call overwrites the previous graph.

    :param mermaid_code: The Mermaid code for the graph.
    :param graph_id: An optional unique graph ID (default is 'mermaid-graph').
    :return: The HTML content for the Mermaid graph with pan and zoom enabled.

    """
    title_label, guid, mermaid_code = parse_mermaid_code(mermaid_str)

    graph_id = f"mermaid-graph-{guid}-{str(uuid.uuid4())[:4]}"
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
        <style>
    /* Style for the diagram container */
    .diagram-container {{
        position: relative;
        width: 100%; /* Adjust the diagram container width */
        height: 500px; /* Set a fixed height for the container */
        margin: 0 auto;
        border: 1px solid #ccc; /* Optional border for visualization */
        overflow: hidden; /* Prevent content overflow outside the container */
    }}

    /* Style for zoom controls */
    .svg-pan-zoom_controls {{
        position: absolute;
        top: 10px;
        right: 10px;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }}
    .svg-pan-zoom_controls button {{
        background-color: #007bff;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 14px;
    }}
    .svg-pan-zoom_controls button:hover {{
        background-color: #0056b3;
    }}
</style>

<div id="{graph_id}-container" class="diagram-container">
    <!-- Mermaid diagram will be dynamically rendered here -->
    {header_html}
    <div id="{graph_id}" class="mermaid">
        {escaped_mermaid_code}
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", () => {{
            // Initialize Mermaid and Pan-Zoom functionality
            const graph_id = "{graph_id}";

            function initializeMermaid(graph_id) {{
                const containerElement = document.getElementById(`${{graph_id}}-container`);

                if (!containerElement) {{
                    console.error(`Container with ID "${{graph_id}}-container" not found.`);
                    return;
                }}

                // Configure Mermaid
                mermaid.initialize({{ startOnLoad: false, logLevel: "debug" }});
                mermaid.init(undefined, `#${{graph_id}}`);

                setTimeout(() => {{
                    const svg = containerElement.querySelector("svg");
                    if (!svg) {{
                        console.error(`SVG not rendered for ID "${{graph_id}}".`);
                        return;
                    }}

                    // Set initial size
                    svg.setAttribute("width", "100%");
                    svg.setAttribute("height", "100%");

                    // Initialize Pan-Zoom
                    const panZoom = svgPanZoom(svg, {{
                        zoomEnabled: true,
                        controlIconsEnabled: false,
                        fit: true,
                        center: true,
                        minZoom: 0.5,
                        maxZoom: 10,
                        contain: true
                    }});

                    // Add custom controls
                    const controlsContainer = document.createElement("div");
                    controlsContainer.className = "svg-pan-zoom_controls";
                    controlsContainer.innerHTML = `
                        <button id="${{graph_id}}-zoom-in">+</button>
                        <button id="${{graph_id}}-zoom-out">-</button>
                        <button id="${{graph_id}}-reset">Reset</button>
                    `;
                    containerElement.appendChild(controlsContainer);

                    // Handle controls
                    document.getElementById(`${{graph_id}}-zoom-in`).addEventListener("click", () => panZoom.zoomIn());
                    document.getElementById(`${{graph_id}}-zoom-out`).addEventListener("click", () => panZoom.zoomOut());
                    document.getElementById(`${{graph_id}}-reset`).addEventListener("click", () => {{
                        panZoom.resetZoom();
                        panZoom.center();
                    }});
                }}, 500);
            }}

            if (typeof mermaid === "undefined") {{
                const script = document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js";
                script.onload = () => initializeMermaid(graph_id);
                document.head.appendChild(script);
            }} else {{
                initializeMermaid(graph_id);
            }}
        }});
    </script>

"""
#
#     return html_content
# This one almost works - no controls and diagram too small
    # html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <style>
#         /* Set consistent sizing and prevent shrinking for the container and parents */
#         html, body, #{graph_id}-wrapper {{
#             margin: 0;
#             padding: 0;
#             height: 100%; /* Ensure the entire root hierarchy respects 100% height */
#             width: 100%;
#         }}
#
#         /* Ensure diagram container maintains full height and prevents overflow */
#         #{graph_id}-container {{
#             position: relative;
#             width: 100%;
#             height: 100%;
#             overflow: hidden; /* Prevent content from breaking layout */
#             display: flex;
#             align-items: center; /* Centers the diagram vertically */
#             justify-content: center; /* Centers the diagram horizontally */
#         }}
#
#         /* Ensure SVG always stretches to match container */
#         #{graph_id} svg {{
#             width: 100%;
#             height: 100%;
#             display: block; /* Avoid unwanted inline space issues */
#         }}
#
#         /* Optional custom pan/zoom controls (if dynamically added) */
#         .svg-pan-zoom_controls {{
#             position: absolute;
#             bottom: 10px; /* Adjust based on desired placement */
#             right: 10px;
#             z-index: 10;
#             display: flex;
#             gap: 5px;
#         }}
#
#         .svg-pan-zoom_controls button {{
#             border: 1px solid #ccc;
#             background-color: #fff;
#             color: #000;
#             padding: 5px 10px;
#             cursor: pointer;
#             font-size: 16px;
#         }}
#
#         .svg-pan-zoom_controls button:hover {{
#             background-color: #f0f0f0;
#         }}
#     </style>
#     </head>
#     <body>
#     <div id="{graph_id}-wrapper">
#         <!-- Title/Heading (optional; include as needed) -->
#         {escaped_header if escaped_header else ""}
#
#         <!-- Mermaid Diagram Container -->
#         <div id="{graph_id}-container">
#             <div id="{graph_id}" class="mermaid">
#                 {escaped_mermaid_code}
#             </div>
#         </div>
#     </div>
#
#     <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
#     <script>
#         document.addEventListener("DOMContentLoaded", () => {{
#                                                              // Define the graph ID dynamically passed via Python
#         const graph_id = "{graph_id}";
#
#         // Function to load external scripts dynamically
#         function loadScript(url, callback) {{
#             const script = document.createElement('script');
#         script.src = url;
#         script.async = true;
#         script.onload = callback;
#         script.onerror = () => console.error("Error loading script:", url);
#         document.head.appendChild(script);
#         }}
#
#         // Function to initialize Mermaid
#         function initializeMermaid(graph_id) {{
#                                               // Look for the container ID generated dynamically by the template
#         const containerElement = document.getElementById(`${{graph_id}}-container`);
#         if (!containerElement) {{
#         console.error(`Container element with id "${{graph_id}}-container" not found.`);
#         return;
#         }}
#
#         // Initialize Mermaid.js with default configuration
#         mermaid.initialize({{ startOnLoad: false, logLevel: "debug" }});
#         mermaid.init(undefined, `#${{graph_id}}`); // Initialize element with id matching `graph_id`
#
#                      // Add a timeout to ensure the SVG is rendered
#         setTimeout(() => {{
#             const svg = containerElement.querySelector("svg");
#
#         // Handle errors if SVG rendering fails
#         if (!svg) {{
#             console.error(`SVG not rendered for ID "${{graph_id}}". Check Mermaid syntax or rendering issues.`);
#         console.log("Container content:", containerElement.innerHTML); // Log the container's content
#         return;
#         }}
#
#         // Set SVG attributes for full container fit
#         svg.setAttribute("width", "100%");
#         svg.setAttribute("height", "100%");
#
#         // Initialize SVG Pan-Zoom functionality
#         const panZoom = svgPanZoom(svg, {{
#         zoomEnabled: true,
#         controlIconsEnabled: true, // Display default controls if enabled
#         fit: true,  // Fit diagram within the container
#         center: true, // Center the diagram
#         minZoom: 0.5, // Prevent too much zooming out
#         maxZoom: 10,  // Prevent extreme zooming in
#                                          contain: true // Keep the diagram fully within bounds
#         }});
#
#         // Optional: Add custom pan/zoom controls dynamically
#             const controlsContainer = document.createElement("div");
#             controlsContainer.classList.add("svg-pan-zoom_controls");
#             controlsContainer.innerHTML = `
#                                         <button id="${{graph_id}}-zoom-in">+</button>
#                                         <button id="${{graph_id}}-zoom-out">-</button>
#                                         <button id="${{graph_id}}-reset">Reset</button>
#                                          `;
#             containerElement.appendChild(controlsContainer);
#
#         // Add event listeners for the custom controls
#         document.getElementById(`${{graph_id}}-zoom-in`).addEventListener("click", () => panZoom.zoomIn());
#         document.getElementById(`${{graph_id}}-zoom-out`).addEventListener("click", () => panZoom.zoomOut());
#         document.getElementById(`${{graph_id}}-reset`).addEventListener("click", () => {{
#                 panZoom.resetZoom();
#                 panZoom.center();
#                 }});
#             }}, 500); // Short delay to ensure SVG rendering is complete
#         }}
#
#         // Load Mermaid.js if not already loaded
#         if (typeof mermaid === "undefined") {{
#             loadScript("https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js", () => {{
#             console.log("Mermaid.js loaded successfully");
#             initializeMermaid(graph_id); // Call initialization after Mermaid.js is loaded
#         }});
#             }} else {{
#                 initializeMermaid(graph_id); // If Mermaid.js is already loaded, proceed immediately
#             }}
#         }});
#     </script>
#
#
#     </body>
#     </html>
#     """





    return html_content

    # // Check if Mermaid and SVG-Pan-Zoom are loaded
    # const loadMermaid = typeof mermaid === "undefined";
    # const loadSvgPanZoom = typeof svgPanZoom === "undefined";
    #
    # if (loadMermaid || loadSvgPanZoom) {{
    #     const promises = [];
    #
    #     // Load Mermaid.js if not already loaded
    #     if (loadMermaid) {{
    #         promises.push(new Promise((resolve) => {{
    #             const script = document.createElement("script");
    #             script.src = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js";
    #             script.onload = resolve;
    #             document.head.appendChild(script);
    #         }}));
    #     }}
    #
    #     // Load SVG-Pan-Zoom if not already loaded
    #     if (loadSvgPanZoom) {{
    #         promises.push(new Promise((resolve) => {{
    #             const script = document.createElement("script");
    #             script.src = "https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js";
    #             script.onload = resolve;
    #             document.head.appendChild(script);
    #         }}));
    #     }}
    #
    #     Promise.all(promises).then(() => initializeMermaid(graph_id));
    # }} else {{
    #     initializeMermaid(graph_id);
    # }}
    # }})();


#     html_content = f"""
# <style>
#     /* Style for the diagram container */
#     .diagram-container {{
#         position: relative;
#         width: 100%; /* Adjust the diagram container width */
#         height: 500px; /* Set a fixed height for the container */
#         margin: 0 auto;
#         border: 1px solid #ccc; /* Optional border for visualization */
#         overflow: hidden; /* Prevent content overflow outside the container */
#     }}
#
#     /* Style for zoom controls */
#     .svg-pan-zoom_controls {{
#         position: absolute;
#         top: 10px;
#         right: 10px;
#         display: flex;
#         flex-direction: column;
#         gap: 5px;
#     }}
#     .svg-pan-zoom_controls button {{
#         background-color: #007bff;
#         color: white;
#         border: none;
#         padding: 5px 10px;
#         border-radius: 3px;
#         cursor: pointer;
#         font-size: 14px;
#     }}
#     .svg-pan-zoom_controls button:hover {{
#         background-color: #0056b3;
#     }}
# </style>
#
# <div id="{graph_id}-container" class="diagram-container">
#     <!-- Mermaid diagram will be dynamically rendered here -->
#     <div id="{graph_id}" class="mermaid">
#         {mermaid_code}
#     </div>
# </div>
#
# <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
#     <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
#     <script>
#         document.addEventListener("DOMContentLoaded", () => {{
#             // Initialize Mermaid and Pan-Zoom functionality
#             const graph_id = "{graph_id}";
#
#             function initializeMermaid(graph_id) {{
#                 const containerElement = document.getElementById(`${{graph_id}}-container`);
#
#                 if (!containerElement) {{
#                     console.error(`Container with ID "${{graph_id}}-container" not found.`);
#                     return;
#                 }}
#
#                 // Configure Mermaid
#                 mermaid.initialize({{ startOnLoad: false, logLevel: "debug" }});
#                 mermaid.init(undefined, `#${{graph_id}}`);
#
#                 setTimeout(() => {{
#                     const svg = containerElement.querySelector("svg");
#                     if (!svg) {{
#                         console.error(`SVG not rendered for ID "${{graph_id}}".`);
#                         return;
#                     }}
#
#                     // Set initial size
#                     svg.setAttribute("width", "100%");
#                     svg.setAttribute("height", "100%");
#
#                     // Initialize Pan-Zoom
#                     const panZoom = svgPanZoom(svg, {{
#                         zoomEnabled: true,
#                         controlIconsEnabled: false,
#                         fit: true,
#                         center: true,
#                         minZoom: 0.5,
#                         maxZoom: 10,
#                         contain: true
#                     }});
#
#                     // Add custom controls
#                     const controlsContainer = document.createElement("div");
#                     controlsContainer.className = "svg-pan-zoom_controls";
#                     controlsContainer.innerHTML = `
#                         <button id="${{graph_id}}-zoom-in">+</button>
#                         <button id="${{graph_id}}-zoom-out">-</button>
#                         <button id="${{graph_id}}-reset">Reset</button>
#                     `;
#                     containerElement.appendChild(controlsContainer);
#
#                     // Handle controls
#                     document.getElementById(`${{graph_id}}-zoom-in`).addEventListener("click", () => panZoom.zoomIn());
#                     document.getElementById(`${{graph_id}}-zoom-out`).addEventListener("click", () => panZoom.zoomOut());
#                     document.getElementById(`${{graph_id}}-reset`).addEventListener("click", () => {{
#                         panZoom.resetZoom();
#                         panZoom.center();
#                     }});
#                 }}, 500);
#             }}
#
#             if (typeof mermaid === "undefined") {{
#                 const script = document.createElement('script');
#                 script.src = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js";
#                 script.onload = () => initializeMermaid(graph_id);
#                 document.head.appendChild(script);
#             }} else {{
#                 initializeMermaid(graph_id);
#             }}
#         }});
#     </script>
#
# """
#
#     return html_content
# This one almost works - no controls and diagram too small
    # html_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <style>
#         /* Set consistent sizing and prevent shrinking for the container and parents */
#         html, body, #{graph_id}-wrapper {{
#             margin: 0;
#             padding: 0;
#             height: 100%; /* Ensure the entire root hierarchy respects 100% height */
#             width: 100%;
#         }}
#
#         /* Ensure diagram container maintains full height and prevents overflow */
#         #{graph_id}-container {{
#             position: relative;
#             width: 100%;
#             height: 100%;
#             overflow: hidden; /* Prevent content from breaking layout */
#             display: flex;
#             align-items: center; /* Centers the diagram vertically */
#             justify-content: center; /* Centers the diagram horizontally */
#         }}
#
#         /* Ensure SVG always stretches to match container */
#         #{graph_id} svg {{
#             width: 100%;
#             height: 100%;
#             display: block; /* Avoid unwanted inline space issues */
#         }}
#
#         /* Optional custom pan/zoom controls (if dynamically added) */
#         .svg-pan-zoom_controls {{
#             position: absolute;
#             bottom: 10px; /* Adjust based on desired placement */
#             right: 10px;
#             z-index: 10;
#             display: flex;
#             gap: 5px;
#         }}
#
#         .svg-pan-zoom_controls button {{
#             border: 1px solid #ccc;
#             background-color: #fff;
#             color: #000;
#             padding: 5px 10px;
#             cursor: pointer;
#             font-size: 16px;
#         }}
#
#         .svg-pan-zoom_controls button:hover {{
#             background-color: #f0f0f0;
#         }}
#     </style>
#     </head>
#     <body>
#     <div id="{graph_id}-wrapper">
#         <!-- Title/Heading (optional; include as needed) -->
#         {escaped_header if escaped_header else ""}
#
#         <!-- Mermaid Diagram Container -->
#         <div id="{graph_id}-container">
#             <div id="{graph_id}" class="mermaid">
#                 {escaped_mermaid_code}
#             </div>
#         </div>
#     </div>
#
#     <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
#     <script>
#         document.addEventListener("DOMContentLoaded", () => {{
#                                                              // Define the graph ID dynamically passed via Python
#         const graph_id = "{graph_id}";
#
#         // Function to load external scripts dynamically
#         function loadScript(url, callback) {{
#             const script = document.createElement('script');
#         script.src = url;
#         script.async = true;
#         script.onload = callback;
#         script.onerror = () => console.error("Error loading script:", url);
#         document.head.appendChild(script);
#         }}
#
#         // Function to initialize Mermaid
#         function initializeMermaid(graph_id) {{
#                                               // Look for the container ID generated dynamically by the template
#         const containerElement = document.getElementById(`${{graph_id}}-container`);
#         if (!containerElement) {{
#         console.error(`Container element with id "${{graph_id}}-container" not found.`);
#         return;
#         }}
#
#         // Initialize Mermaid.js with default configuration
#         mermaid.initialize({{ startOnLoad: false, logLevel: "debug" }});
#         mermaid.init(undefined, `#${{graph_id}}`); // Initialize element with id matching `graph_id`
#
#                      // Add a timeout to ensure the SVG is rendered
#         setTimeout(() => {{
#             const svg = containerElement.querySelector("svg");
#
#         // Handle errors if SVG rendering fails
#         if (!svg) {{
#             console.error(`SVG not rendered for ID "${{graph_id}}". Check Mermaid syntax or rendering issues.`);
#         console.log("Container content:", containerElement.innerHTML); // Log the container's content
#         return;
#         }}
#
#         // Set SVG attributes for full container fit
#         svg.setAttribute("width", "100%");
#         svg.setAttribute("height", "100%");
#
#         // Initialize SVG Pan-Zoom functionality
#         const panZoom = svgPanZoom(svg, {{
#         zoomEnabled: true,
#         controlIconsEnabled: true, // Display default controls if enabled
#         fit: true,  // Fit diagram within the container
#         center: true, // Center the diagram
#         minZoom: 0.5, // Prevent too much zooming out
#         maxZoom: 10,  // Prevent extreme zooming in
#                                          contain: true // Keep the diagram fully within bounds
#         }});
#
#         // Optional: Add custom pan/zoom controls dynamically
#             const controlsContainer = document.createElement("div");
#             controlsContainer.classList.add("svg-pan-zoom_controls");
#             controlsContainer.innerHTML = `
#                                         <button id="${{graph_id}}-zoom-in">+</button>
#                                         <button id="${{graph_id}}-zoom-out">-</button>
#                                         <button id="${{graph_id}}-reset">Reset</button>
#                                          `;
#             containerElement.appendChild(controlsContainer);
#
#         // Add event listeners for the custom controls
#         document.getElementById(`${{graph_id}}-zoom-in`).addEventListener("click", () => panZoom.zoomIn());
#         document.getElementById(`${{graph_id}}-zoom-out`).addEventListener("click", () => panZoom.zoomOut());
#         document.getElementById(`${{graph_id}}-reset`).addEventListener("click", () => {{
#                 panZoom.resetZoom();
#                 panZoom.center();
#                 }});
#             }}, 500); // Short delay to ensure SVG rendering is complete
#         }}
#
#         // Load Mermaid.js if not already loaded
#         if (typeof mermaid === "undefined") {{
#             loadScript("https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js", () => {{
#             console.log("Mermaid.js loaded successfully");
#             initializeMermaid(graph_id); // Call initialization after Mermaid.js is loaded
#         }});
#             }} else {{
#                 initializeMermaid(graph_id); // If Mermaid.js is already loaded, proceed immediately
#             }}
#         }});
#     </script>
#
#
#     </body>
#     </html>
#     """

    

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

    payload = construct_mermaid_web(mermaid_str)

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
