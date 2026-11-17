"""
Generate VHS tape scripts for all 7 Coco Pharmaceuticals Business Value episodes
and execute them using Charm's `vhs` to create pixel-perfect, 1080p full-color
terminal video walkthroughs.
"""

import subprocess
import shutil
from pathlib import Path
from episode_specs import EPISODES

TAPES_DIR = Path(__file__).parent / "tapes"
TAPES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_BASE_DIR = Path(__file__).parent / "output"


def build_tape_content(ep_id: str, episode) -> str:
    ep_num = episode.episode_number
    username = episode.persona_username
    output_mp4 = OUTPUT_BASE_DIR / f"episode{ep_num}" / "videos" / f"episode_{ep_num}_walkthrough.mp4"
    output_mp4.parent.mkdir(parents=True, exist_ok=True)

    header = f"""# VHS Tape: Episode {ep_num} - {episode.title}
# Lead Persona: {episode.lead_persona} ({username})
# Output: 1080p TrueColor MP4 Terminal Walkthrough

Output "{output_mp4}"

Set Shell "bash"
Set FontSize 18
Set FontFamily "Menlo"
Set Width 1920
Set Height 1080
Set Padding 20
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set WindowBarSize 40
Set MarginFill "#1e1e2e"
Set BorderRadius 10
Set TypingSpeed 50ms

Type "unset NO_COLOR && export COLORTERM=truecolor TERM=xterm-256color FORCE_COLOR=1 EGERIA_USER={username} && clear"
Enter
Sleep 500ms

# Launch My Profile as {username}
Type "uv run my_profile"
Enter
Sleep 3.5s
"""

    if ep_id == "episode1":
        body = """
# Welcome Splash Screen (Faith Broker - HR & Data Privacy Officer)
Sleep 7s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Privacy Role & Team Hierarchy
# Focus on Governance Council and HR Leadership
Tab 1
Sleep 2s
Down 2
Sleep 2s
Enter
Sleep 4s
Escape
Sleep 2s

# Scene 3: Subject Access Request (SAR) & PII Lineage
# Select Catalogs / Shop for Data from Other Functions
Tab 3
Down 6
Sleep 1s
Enter
Sleep 4s
Type "Clinical"
Sleep 1s
Enter
Sleep 3s
Escape
Sleep 2s

# Navigate to My Network Graph
Tab 3
Down 1
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 2s

# Scene 4: Real-Time Privacy Stewardship & Feedback
# Open Leave Feedback modal
Tab 3
Down 3
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 2s

# Focus on To-Dos table
Tab 4
Ctrl+T
Sleep 3s
Escape
Sleep 4s
"""
    elif ep_id == "episode2":
        body = """
# Welcome Splash Screen (Peter Profile - Lead Data Steward)
Sleep 6s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Managing Curation To-Dos
Tab 4
Sleep 1.5s
Ctrl+T
Sleep 4s
Down 2
Sleep 2s
Escape
Sleep 2s

# Scene 3: Real-Time Annotation & Discussion Threads
Ctrl+O
Sleep 4s
Ctrl+N
Sleep 3s
Type "Verified ISO 27001 mapping for clinical trial schemas"
Sleep 2s
Escape
Sleep 2s
Escape
Sleep 2s

# Scene 4: Earning Karma Points & Community Leadership
Ctrl+B
Sleep 4s
Escape
Sleep 2s
Tab 1
Sleep 2s
Down 1
Sleep 4s
"""
    elif ep_id == "episode3":
        body = """
# Welcome Splash Screen (Dr. Tessa Tube - Lead Clinical Researcher)
Sleep 7s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Shopping for Certified Clinical Data Products
Tab 3
Down 6
Sleep 1s
Enter
Sleep 4s
Type "Cohort"
Sleep 1s
Enter
Sleep 4s

# Scene 3: Governed Subscription Requests & Usage Terms
Ctrl+L
Sleep 4s
Escape
Sleep 2s
Ctrl+U
Sleep 4s
Escape
Sleep 2s
Escape
Sleep 2s

# Scene 4: Cross-Functional Research Collaboration
Tab 3
Down 2
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 4s
"""
    elif ep_id == "episode4":
        body = """
# Welcome Splash Screen (Stew Faster - Manufacturing General Manager)
Sleep 5s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Plant Manager Dashboard & Roles
Tab 1
Sleep 2s
Down 2
Sleep 3s

# Scene 3: Exploring Technology Types & Factory Catalogs
Tab 3
Down 7
Sleep 1s
Enter
Sleep 5s
Down 2
Sleep 2s
Up 1
Sleep 2s
Escape
Sleep 2s

# Scene 4: Collaborative Operational Feedback & Actions
Tab 3
Down 3
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 3s
"""
    elif ep_id == "episode5":
        body = """
# Welcome Splash Screen (Erin Overview - Enterprise Information Architect)
Sleep 6s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Architecture Cockpit & Communities Navigation
Tab 3
Down 2
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 2s

# Scene 3: Browsing Unified Glossary & Term Dictionaries
Tab 3
Down 6
Sleep 1s
Enter
Sleep 4s
Type "Architecture"
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 2s

# Scene 4: Graph Visualization of Architectural Dependencies
Tab 3
Down 1
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 3s
"""
    elif ep_id == "episode6":
        body = """
# Welcome Splash Screen (Sidney Seeker - Lead Fraud Investigator)
Sleep 6s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Investigator Workspace & Security Team Drill-Down
Tab 1
Sleep 2s
Down 2
Sleep 3s

# Scene 3: Tracing Payment Anomalies with Lineage & Comments
Ctrl+O
Sleep 4s
Escape
Sleep 2s
Tab 4
Ctrl+T
Sleep 3s
Escape
Sleep 2s

# Scene 4: Uncovering Shadow IT in the Network Graph
Tab 3
Down 1
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 3s
"""
    else:  # episode7
        body = """
# Welcome Splash Screen (Jules Keeper - Chief Data Officer)
Sleep 6s

# Dismiss Splash Screen into Main Dashboard
Enter
Sleep 3.5s

# Scene 2: Executive Cockpit Walkthrough & Portfolio Health
Tab 1
Sleep 2s
Down 2
Sleep 3s

# Scene 3: CFO Perspective - Quantifying Data ROI & Risk Reduction
Tab 3
Down 9
Sleep 1s
Enter
Sleep 3s
Escape
Sleep 2s

# Scene 4: Community Engagement & Collaborative Governance
Tab 3
Down 2
Sleep 1s
Enter
Sleep 4s
Escape
Sleep 2s
Tab 3
Down 3
Sleep 1s
Enter
Sleep 3s
Escape
Sleep 3s
"""

    return header + body


def generate_all_tapes():
    print("Generating VHS Tape scripts for Episodes 1 through 7...")
    for ep_id, ep in EPISODES.items():
        tape_path = TAPES_DIR / f"{ep_id}_walkthrough.tape"
        content = build_tape_content(ep_id, ep)
        tape_path.write_text(content)
        print(f"  ✓ Created {tape_path.name}")


def run_vhs(ep_id: str = "all"):
    if not shutil.which("vhs"):
        print("[ERROR] 'vhs' CLI is not installed. Please install with 'brew install vhs'.")
        return False

    targets = [ep_id] if ep_id != "all" else list(EPISODES.keys())
    for target in targets:
        tape_path = TAPES_DIR / f"{target}_walkthrough.tape"
        if not tape_path.exists():
            print(f"[WARN] Tape {tape_path.name} not found. Generating...")
            tape_path.write_text(build_tape_content(target, EPISODES[target]))

        print(f"\n▶ Running VHS recording for {target}: {tape_path.name}...")
        res = subprocess.run(["vhs", str(tape_path)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  ✓ Successfully recorded {target} terminal walkthrough MP4!")
        else:
            print(f"  ✗ VHS failed for {target}:\n{res.stderr}")
    return True


if __name__ == "__main__":
    import sys
    generate_all_tapes()
    target_ep = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_vhs(target_ep)
