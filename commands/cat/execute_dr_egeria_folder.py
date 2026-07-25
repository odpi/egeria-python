"""
Execute all Dr. Egeria markdown files in a folder, following the load order in README.md if present.
"""
import os
import sys
import click
import re
import asyncio
from loguru import logger
from rich.console import Console

from pyegeria.core._exceptions import PyegeriaException, print_basic_exception
from pyegeria.core.config import settings
from md_processing.dr_egeria import process_md_file_v2
from pyegeria import EgeriaTech

# Configure logging
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="WARNING", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="WARNING", format=log_format,
           colorize=True)

# Load configuration
app_config = settings.Environment

EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", app_config.egeria_view_server)
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", app_config.egeria_view_server_url)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", settings.Environment.egeria_width or 190))

console = Console(width=EGERIA_WIDTH)

def get_load_order(folder_path: str) -> list[str]:
    """Extract load order from README.md if it exists."""
    readme_path = os.path.join(folder_path, "README.md")
    if not os.path.exists(readme_path):
        return []
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Look for "## Load order" section and then a code block
    match = re.search(r'## Load order\s+.*?```\s+(.*?)\s+```', content, re.DOTALL)
    if not match:
        return []
    
    lines = match.group(1).splitlines()
    files = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Extract filename - assuming it's the last word on the line
        parts = line.split()
        if parts:
            files.append(parts[-1])
    return files

async def run_folder(folder_path: str, directive: str, client: EgeriaTech, 
                     parse_summary: str, attribute_logs: str, usage_level: str,
                     summary_only: bool, debug: bool) -> None:
    """Execute all files in the folder."""
    files = get_load_order(folder_path)
    
    if not files:
        # Fallback to all .md files in alphabetical order, excluding README.md
        files = sorted([f for f in os.listdir(folder_path) 
                        if f.endswith(".md") and f.lower() != "readme.md"])
        console.print(f"[yellow]No load order found in README.md, using alphabetical order.[/yellow]")
    else:
        console.print(f"[green]Following load order from README.md[/green]")

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        if not os.path.exists(file_path):
            console.print(f"[red]File not found: {file_path}[/red]")
            continue
            
        console.print(f"\n[bold blue]Processing {filename}...[/bold blue]")
        try:
            await process_md_file_v2(
                input_file=file_path,
                output_folder="",
                directive=directive,
                client=client,
                parse_summary=parse_summary,
                attribute_logs=attribute_logs,
                usage_level=usage_level,
                summary_only=summary_only,
                debug=debug,
            )
        except Exception as e:
            console.print(f"[red]Error processing {filename}: {e}[/red]")
            if debug:
                console.print_exception()

@click.command("execute_dr_egeria_folder", help="Execute all Dr. Egeria markdown files in a folder.")
@click.argument("folder_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--directive", default="validate", help="How to process the files (display/validate/process).",
              type=click.Choice(["display", "validate", "process"], case_sensitive=False))
@click.option("--validate", "do_validate", is_flag=True, default=False, help="Shortcut for --directive validate")
@click.option("--process", "do_process", is_flag=True, default=False, help="Shortcut for --directive process")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--parse-summary", default="none", help="When to show parse summaries",
              type=click.Choice(["all", "errors", "none"], case_sensitive=False))
@click.option("--attribute-logs", default="info", help="Per-attribute log verbosity",
              type=click.Choice(["debug", "info", "none"], case_sensitive=False))
@click.option("--advanced", is_flag=True, default=False, help="Use Advanced usage level")
@click.option("--summary-only", is_flag=True, default=False, help="Only display the summary table")
@click.option("--debug", is_flag=True, default=False, help="Print each Egeria API request URL and body")
def main(folder_path: str, directive: str, do_validate: bool, do_process: bool,
         server: str, url: str, userid: str, user_pass: str, 
         parse_summary: str, attribute_logs: str, advanced: bool,
         summary_only: bool, debug: bool) -> None:
    
    if do_process:
        directive = "process"
    elif do_validate:
        directive = "validate"
        
    usage_level = "Advanced" if advanced else "Basic"
    
    try:
        client = EgeriaTech(server, url, userid, user_pass)
        client.create_egeria_bearer_token()
        
        asyncio.run(run_folder(
            folder_path=folder_path,
            directive=directive,
            client=client,
            parse_summary=parse_summary,
            attribute_logs=attribute_logs,
            usage_level=usage_level,
            summary_only=summary_only,
            debug=debug
        ))
        
    except PyegeriaException as e:
        console.print_exception()
        print_basic_exception(e)
    except Exception as e:
        console.print_exception()
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
