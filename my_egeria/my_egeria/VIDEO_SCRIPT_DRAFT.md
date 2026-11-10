# My Profile — Video Blog Script (DRAFT)

**Working title:** "Meeting Egeria Through My Profile — Callie Quartile, Data Scientist at Coco Pharmaceuticals"  
**Target length:** ~4.5 to 5 minutes (≈650 spoken words)  
**Format:** In-character video blog set at Coco Pharmaceuticals, following the established style of the Jules Keeper video series by Mandy Chessell (as seen on prd-associates.com and YouTube). Talking head / voice-over with live terminal screen capture of `my_profile.py` (`MyProfileApp`).  
**Presenter persona:** Callie Quartile, Data Scientist at Coco Pharmaceuticals (with cameos/references to Jules Keeper, Tessa Tube, and Peter Profile).  

---

## 0. Cold open (0:00 – 0:20)

**[VISUAL]** Callie Quartile to camera, warm and engaging, against a modern office background or Coco Pharmaceuticals title card: *"Better Data for Everyone — Powered by Egeria"*.

**CALLIE:**
> Hi, I'm Callie Quartile. I'm a data scientist here at Coco Pharmaceuticals. When our Chief Data Officer, Jules Keeper, rolled out our *"better data for everyone"* initiative, my biggest question was: how do I navigate this vast ocean of metadata without getting bogged down in complexity? Where do I actually start?
> It turns out, I start with **me**.

**[LOWER THIRD]** Callie Quartile — Data Scientist, Coco Pharmaceuticals  
**[TITLE CARD]** Meeting Egeria Through My Profile

---

## 1. The Context: One Persona, One Workspace (0:20 – 0:50)

**[VISUAL]** Slide animation / graphic: Callie in the center connected to teams, clinical trial projects, data products, glossaries, governance roles, and daily to-dos.

**CALLIE:**
> In a modern enterprise like Coco Pharmaceuticals, open metadata isn't just an abstract catalogue—it's the living fabric of how we work. Egeria knows my appointed roles, the clinical research teams I collaborate with, my active projects, and the governed data assets I rely on.
> But having that information scattered across separate systems slows everyone down. We needed a single, fast, keyboard-driven cockpit where any team member can see their world, keep it current, and take action.
> That workspace is **My Profile**.

---

## 2. Launch & Parallel Startup (0:50 – 1:20)

**[VISUAL]** Terminal window. Clean dark theme. Type `uv run my_profile` (or `python -m my_egeria.my_profile`).  
The splash screen appears instantly with: *"Welcome to My Profile for Egeria Users, calliequartile!"* and buttons for **Continue to App** and **Change User**.

**CALLIE:**
> My Profile is a terminal application built on Textual and pyegeria. When you launch it, there's no waiting around. While the splash screen greets you, it's already querying the Egeria platform asynchronously in the background. By the time you hit **Continue**, your full profile is loaded and ready in memory.
> If I'm collaborating at a colleague's desk or testing access permissions, **Change User** lets me switch identities on the fly with live credential validation. And if our server ever needs a restart, built-in connection retry screens keep things seamless.

**[ON-SCREEN CALLOUT]** "Async background loading • Live credential validation • Instant startup"

---

## 3. The Main Dashboard Tour (1:20 – 2:05)

**[VISUAL]** Main Dashboard renders. The header prominently displays:  
`Egeria — User: calliequartile | Karma Points: 120 | 09:30:00`  
Camera highlights the structured grid panels:
- Top Left: **User Associations** & **My Collections**
- Top Right: **Other Functions** menu list
- Middle: **Roles** (with team drill-down note) & **Teams**
- Activity Center: **Blogs**, **Journal**, and **To-Dos**
- Bottom: **User Identity** and **Projects**
- Footer: Shortcut key bindings (`Ctrl+T` Edit Table, `Ctrl+O` Comments, `Ctrl+N` Add Comment, `Ctrl+K` Bookmark Row, `Ctrl+B` Bookmarks, `Ctrl+F` Feedback, `q` Quit).

**CALLIE:**
> Here is my daily cockpit. Every single panel is populated live from Egeria.
> At the top, I have my **User Associations** and **Collections**, organizing the assets I care about.
> In the middle, I can see my appointed **Roles** and **Teams**. Notice this tip: pressing Enter on a Team Leader or Member role immediately opens **My Team**, showing everyone I'm working with and their responsibilities.
> Over here is my daily work stream: my **Blogs**, personal **Journal**, and **To-Dos**.
> And at the bottom, my **User Identity** mappings and active **Projects** across Coco Pharmaceuticals.

**[ON-SCREEN CALLOUT]** "Live metadata synchronization • Role & Team drill-down • Karma point tracking"

---

## 4. Real-Time Curation: To-Dos, Comments & Bookmarks (2:05 – 2:50)

**[VISUAL]**  
1. Callie navigates to the **To-Dos** table, highlights a row, and presses `Ctrl+T`. The **Edit Selected Table** screen opens; she clicks **Add Row** and enters: *"Review clinical trial patient cohort data quality"*. The new to-do appears instantly on the dashboard.
2. Selects an asset row, presses `Ctrl+O` to view comments, then `Ctrl+N` to add a comment: *"Verified schema alignment with Dr. Tessa Tube"*.
3. Presses `Ctrl+K` to bookmark the row, then presses `Ctrl+B` to show the **My Bookmarks** management screen.

**CALLIE:**
> Metadata is only valuable if it's kept fresh and actionable. With simple keystrokes, I can curate my workspace without leaving the keyboard.
> Hitting **Ctrl+T** lets me edit any highlighted table—adding tasks from morning stand-ups or updating project milestones.
> **Ctrl+O** and **Ctrl+N** allow me to view and add threaded discussions directly onto elements. That means conversations stay anchored to the data asset or task itself, instead of getting lost in chat channels.
> And with **Ctrl+K** and **Ctrl+B**, I bookmark critical elements for instant one-touch retrieval.

**[KEY SHORTCUT OVERLAYS]**  
`Ctrl+T` Edit Table • `Ctrl+O` Show Comments • `Ctrl+N` Add Comment • `Ctrl+K` Bookmark Row • `Ctrl+B` Bookmarks

---

## 5. The Hero Workflow: Shopping for Governed Data (2:50 – 3:50)

**[VISUAL]**  
1. Callie selects **Other Functions** → **Catalogs/Shop for Data**.
2. The **Shop for Data** screen opens, showcasing:
   - **Business Domain** & **Root Collections**
   - **Glossaries** (terms and definitions)
   - **Digital Product Catalog** (data products)
   - **Data Dictionaries** (schemas and specifications)
3. Callie searches for *"Clinical Trial Metrics"*, selects the data product, and presses `Ctrl+L` (**Sample Data**). A sample data table appears with real distribution values.
4. Convinced, she presses `Ctrl+U` (**Subscribe**). The **Create Subscription Request** modal opens. She enters her purpose (*"Efficacy analysis for Coco treatment trial"*), selects subscription terms, and submits.
5. Back in **Other Functions** → **Subscriptions**, the new active subscription is displayed.

**CALLIE:**
> Now for my absolute favorite feature: **Shop for Data**.
> As a data scientist, finding trusted, high-quality data used to take weeks of asking around. Here, Egeria unifies our Business Domains, Glossaries, Data Dictionaries, and Digital Product Catalogs into a single curated marketplace.
> I can search across terms, inspect schemas, and press **Ctrl+L** to **sample** the data right in the terminal before making any commitments.
> Once I know it's what I need, **Ctrl+U** lets me submit a formal **Subscription Request**. Egeria routes the request under governance policy so data owners understand who is using their data, for what purpose, and under what terms.
> In a matter of seconds, governed access is requested, approved, and tracked in **Subscriptions**.

**[ON-SCREEN CALLOUT]** "Unified Catalog Search • Instant Data Sampling (`Ctrl+L`) • Governed Subscriptions (`Ctrl+U`)"

---

## 6. Collaboration, Networks & Technology Types (3:50 – 4:30)

**[VISUAL]**  
1. Callie selects **Other Functions** → **My Network**. A visual Mermaid graph renders her organizational network, peers, and collaborators.
2. Selects **Work with Communities** → **Communities Screen**, showing Coco Pharmaceuticals Clinical Research Community, its leaders, and resources.
3. Presses `Ctrl+F` to demonstrate the instant **Leave Feedback** dialog.
4. Selects **Technology Types**, showing automated curation templates and governance action processes.

**CALLIE:**
> Beyond data shopping, My Profile connects you to the wider community.
> **My Network** visualizes your collaboration web and reporting structures directly in the terminal.
> **Work with Communities** lets you engage with domain working groups across Coco Pharmaceuticals.
> Pressing **Ctrl+F** lets you leave feedback anywhere in the app, logging suggestions straight to Egeria.
> And for engineers and data stewards, the **Technology Types** screen reveals automated curation templates and processes that Egeria can trigger across your tech stack.

---

## 7. Wrap-up & Call to Action (4:30 – 5:00)

**[VISUAL]** Callie back on camera, smiling and enthusiastic.

**CALLIE:**
> That is **My Profile** in action: a fast, intuitive, and governed personal cockpit that turns enterprise metadata into everyday productivity.
> When Jules Keeper said *"better data for everyone"*, this is what it looks like on the ground: empowered individuals, transparent collaboration, and trustworthy data at our fingertips.
> `my_profile` is fully open source as part of the `egeria-python` ecosystem. Try it out in your terminal, connect it to the Coco Pharmaceuticals sample environment, and see how easy it is to make Egeria work for you.
> Thanks for watching, and happy data exploring!

**[END CARD & LINKS]**
- **Egeria Project:** https://egeria-project.org
- **Egeria Python SDK & TUI:** https://github.com/odpi/egeria-python (`my_egeria` package)
- **PRD Associates & Video Series:** https://www.prd-associates.com
- **Run Locally:** `uv run my_profile` or `uv run serve_my_profile`
- *"Catch up on the Jules Keeper Coco Pharmaceuticals Video Series on YouTube"*

---

## Production & Recording Notes

- **Persona & Tone:** Callie Quartile (Data Scientist). Warm, articulate, practical, and solution-focused. She speaks colleague-to-colleague, demonstrating real workflow gains rather than reading a software feature manual.
- **Visual Styling:** 
  - Standard 1920×1080 resolution.
  - Large monospace terminal font (≥18pt, e.g., JetBrains Mono, Fira Code) running `my_profile.tcss` theme.
  - Smooth pan-and-zoom to spotlight active widgets and dialogs during keypresses.
- **Timing & Keystrokes:** Pause 0.5s before striking hotkeys (`Ctrl+T`, `Ctrl+O`, `Ctrl+N`, `Ctrl+K`, `Ctrl+B`, `Ctrl+L`, `Ctrl+U`, `Ctrl+F`) with clear animated key badges on screen.
- **Demo Data Environment:** Run against standard Coco Pharmaceuticals demo metadata (users: `calliequartile`, `peterprofile`, `juleskeeper`, `tessatube`). Pre-seed sample to-dos, comments, clinical trial data products, and community memberships.
- **Browser Web-TUI Option:** Mention or show a 5-second b-roll clip of `serve_my_profile` running inside a web browser to highlight web-socket accessibility.
- **Sample Social / Video Description Copy:**
  > Meet My Profile! 🚀 The interactive terminal cockpit for Egeria users. In this video, Callie Quartile (Data Scientist at Coco Pharmaceuticals) demonstrates how she navigates her daily tasks, manages teams and to-dos, explores glossaries, samples data products, and subscribes to governed datasets in seconds.
  >
  > 📺 Part of the Coco Pharmaceuticals Egeria Video Series.
  > 🔗 Learn more: https://egeria-project.org | https://www.prd-associates.com
  > 💻 Open Source: github.com/odpi/egeria-python
  > #Egeria #DataGovernance #OpenMetadata #Python #Textual #DataMesh #CocoPharmaceuticals
