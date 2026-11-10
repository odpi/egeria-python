# My Profile — Video Blog Script (DRAFT)

**Series Context:** *Coco Pharmaceuticals Data Governance Journey* — Practitioner Companion to Jules Keeper's Video Blogs  
**Working title:** "Meeting Egeria Through My Profile — Callie Quartile, Data Scientist at Coco Pharmaceuticals"  
**Target length:** ~4.5 to 5 minutes (≈650 spoken words)  
**Format:** In-character video blog set at Coco Pharmaceuticals, following the established narrative and visual style of Mandy Chessell's Jules Keeper video series (as featured on [prd-associates.com](https://www.prd-associates.com) and YouTube). Combines direct-to-camera presenter segments with live terminal screen recordings of `my_profile.py` (`MyProfileApp`).  
**Presenter persona:** Callie Quartile, Data Scientist (Clinical Trials & AI Pilot Teams) at Coco Pharmaceuticals, with contextual references to Jules Keeper (CDO), Dr. Tessa Tube (Lead Researcher), Peter Profile (Information Analyst), and Faith Broker (Privacy Officer).  

---

## 0. Cold Open & Introduction (0:00 – 0:25)

**[VISUAL]** Callie Quartile to camera in her lab/office at Coco Pharmaceuticals. Warm, engaging, and practical.  
**[SLIDE OVERLAY]** Coco Pharmaceuticals title card: *"Better Data for Everyone — Powered by Egeria"*.

**CALLIE:**
> Hi, I'm Callie Quartile. I'm a data scientist here at Coco Pharmaceuticals, working across our Clinical Trials research and AI Pilot teams.
> If you've been following Jules Keeper's video blogs, you've heard our Chief Data Officer talk about his mission to establish business-led data governance without creating bureaucratic roadblocks.
> But as someone building cancer research models on patient cohorts, my immediate question was: how does Jules's *"better data for everyone"* initiative help me get my daily work done? Where do I actually start?
> It turns out, I start with **me**.

**[LOWER THIRD]** Callie Quartile — Data Scientist, Coco Pharmaceuticals  
**[TITLE CARD]** *Meeting Egeria Through My Profile: The Practitioner's Cockpit*

---

## 1. The Context: Operationalizing Governance Roles (0:25 – 0:55)

**[VISUAL]** Conceptual diagram / visual slide: Callie at the center, linked to clinical research teams, governance roles, glossaries, digital data products, and active to-dos.

**CALLIE:**
> In his recent video on *Establishing Data Governance*, Jules pointed out that governance policies on paper remain passive until you attach responsibilities to **named roles** with real people appointed to them.
> Egeria already knows the appointed roles I hold, the clinical trial teams I collaborate with under Dr. Tessa Tube, the data definitions curated by Peter Profile, and the privacy classifications set by Faith Broker.
> But having that information fragmented across multiple tools slows us down. We needed one fast, interactive, keyboard-driven cockpit where any team member can see their governance ecosystem, keep it up to date, and take immediate action.
> That workspace is **My Profile**.

---

## 2. Launch & Parallel Background Startup (0:55 – 1:25)

**[VISUAL]** Terminal window in clean dark theme. Callie types `uv run my_profile` (or `python -m my_egeria.my_profile`).  
The splash screen displays: *"Welcome to My Profile for Egeria Users, calliequartile!"* with action buttons **Continue to App** and **Change User**.

**CALLIE:**
> My Profile is a terminal application built with Textual and pyegeria. When you launch it, there's no waiting around.
> While this welcome screen greets you, the application is already querying the Egeria metadata highway asynchronously in the background. By the time you hit **Continue**, your full profile, role appointments, and collections are already loaded in memory.
> And if I'm pairing with Peter Profile or auditing permissions with Faith Broker, **Change User** lets us switch identities right from the start with live credential validation.

**[ON-SCREEN CALLOUT]** "Async background profile loading • Live credential validation • Instant keyboard response"

---

## 3. The Main Dashboard Tour (1:25 – 2:10)

**[VISUAL]** Main Dashboard loads seamlessly.  
Header bar highlights: `Egeria — User: calliequartile | Karma Points: 120 | 09:30:00`  
Camera pans through the structured grid layout:
- **Top Left:** User Associations & My Collections
- **Top Right:** Other Functions Menu
- **Middle Section:** Roles (with Team drill-down tip) & Teams
- **Activity Stream:** Blogs, Personal Journal, and Active To-Dos
- **Bottom Section:** User Identity mappings & Research Projects
- **Footer:** Global hotkeys (`Ctrl+T` Edit, `Ctrl+O` Comments, `Ctrl+N` Add Comment, `Ctrl+K` Bookmark, `Ctrl+B` Bookmarks, `Ctrl+F` Feedback, `q` Quit).

**CALLIE:**
> Here is my daily home base. Every single panel is synchronized live with Egeria.
> At the top, my **User Associations** and **Collections** organize the clinical datasets and glossaries I care about.
> In the middle, you see my appointed **Roles** and **Teams**. Notice how governance comes alive here: pressing Enter on my Clinical Trials team role instantly opens **My Team**, showing colleagues like Tessa Tube and Tanya Tidie along with their active responsibilities.
> Down here is my daily activity stream: team **Blogs**, my personal **Journal**, and my **To-Dos**.
> And at the top right, Egeria tracks my **Karma Points**, recognizing active curation and collaboration across Coco Pharmaceuticals!

**[ON-SCREEN CALLOUT]** "Live metadata synchronization • Role & Team drill-down • Automated Karma recognition"

---

## 4. Real-Time Curation: To-Dos, Comments & Bookmarks (2:10 – 2:55)

**[VISUAL]**  
1. Callie navigates to the **To-Dos** panel, highlights a row, and presses `Ctrl+T`. The **Edit Selected Table** dialog opens; she adds: *"Verify hospital cohort schema with Peter Profile"*. The row updates live on the dashboard.
2. Highlights an asset, presses `Ctrl+O` to view comments, then `Ctrl+N` to add a comment: *"Confidence score 0.95 verified against clinical laboratory assay standards"*.
3. Presses `Ctrl+K` to bookmark the item, then `Ctrl+B` to display the **My Bookmarks** management screen.

**CALLIE:**
> Data governance only works if metadata is maintained as part of our normal flow of work, not as an afterthought.
> Pressing **Ctrl+T** lets me edit any highlighted table in place—adding action items from morning stand-ups or updating project milestones.
> With **Ctrl+O** and **Ctrl+N**, threaded discussions attach directly to the metadata asset or task itself. Instead of losing critical context in email threads, Dr. Tube and I keep our clinical trial discussions permanently linked to the data.
> And with **Ctrl+K** and **Ctrl+B**, I can bookmark key assets and retrieve them instantly with a single keystroke.

**[KEY SHORTCUT OVERLAYS]**  
`Ctrl+T` Edit Table • `Ctrl+O` Show Comments • `Ctrl+N` Add Comment • `Ctrl+K` Bookmark Row • `Ctrl+B` Bookmarks

---

## 5. The Hero Workflow: Shopping for Governed Data Products (2:55 – 3:55)

**[VISUAL]**  
1. Callie opens **Other Functions** → **Catalogs / Shop for Data**.
2. The catalog marketplace renders:
   - **Business Domains** & **Root Collections**
   - **Glossaries** (Business concepts curated by Erin Overview & Peter Profile)
   - **Data Dictionaries** (Physical schemas & clinical data specifications)
   - **Digital Product Catalog** (Certified research data products)
3. Callie searches for *"Patient Cohort Treatment Efficacy"*, selects the data product, and presses `Ctrl+L` (**Sample Data**). A clean sample data preview opens displaying distribution metrics and confidentiality tags.
4. Confident in the data quality, she presses `Ctrl+U` (**Subscribe**). The **Create Subscription Request** modal opens. She enters her purpose (*"AI oncology treatment response modeling"*), agrees to governance terms, and submits.
5. She navigates to **Other Functions** → **Subscriptions**, where the new active governed subscription appears.

**CALLIE:**
> Now for the most powerful feature in my workflow: **Shop for Data**.
> Before Jules Keeper established our open metadata catalog, finding trusted clinical data meant weeks of meetings and manual approvals. Here, Egeria brings together Business Domains, Glossaries, Data Dictionaries, and Digital Product Catalogs into a unified data marketplace.
> I can explore standardized terminology, verify classifications, and hit **Ctrl+L** to **sample** the dataset right in my terminal to ensure it fits my AI model requirements.
> When it's right, **Ctrl+U** lets me submit a formal **Subscription Request**. Egeria ensures Faith Broker's privacy rules and compliance policies are satisfied, giving data owners full visibility into who is using their data and why.
> In less than sixty seconds, governed access is requested, validated, and tracked in **Subscriptions**.

**[ON-SCREEN CALLOUT]** "Unified Data Marketplace • Instant Data Sampling (`Ctrl+L`) • Governed Subscriptions (`Ctrl+U`)"

---

## 6. Collaboration, Networks & Technology Curation (3:55 – 4:35)

**[VISUAL]**  
1. Callie navigates to **Other Functions** → **My Network**. An interactive Mermaid graph visualizes her cross-functional network across Clinical Trials, AI Pilot, and Governance teams.
2. Selects **Work with Communities**, showcasing the *Coco Pharmaceuticals Clinical Research Community*.
3. Presses `Ctrl+F` to pop up the in-app **Leave Feedback** dialog.
4. Briefly shows **Technology Types**, displaying automated curation templates and governance action processes.

**CALLIE:**
> My Profile also strengthens our human network across Coco Pharmaceuticals.
> **My Network** visualizes collaboration graphs and reporting relationships across departments.
> **Work with Communities** connects us to cross-functional working groups, like our Oncology Research and Sustainability circles.
> If I notice something that needs improvement, pressing **Ctrl+F** lets me log feedback directly into Egeria from anywhere in the app.
> And for our integration architects like Bob Nitter, the **Technology Types** screen displays the automated governance action templates Egeria executes behind the scenes.

---

## 7. Wrap-Up & Call to Action (4:35 – 5:00)

**[VISUAL]** Callie back on camera, smiling and enthusiastic.

**CALLIE:**
> That is **My Profile**: a fast, intuitive, and governed personal cockpit that turns enterprise metadata into everyday productivity.
> When Jules Keeper says *"better data for everyone"*, this is what it looks like in practice: researchers and data scientists spending less time searching for data and more time discovering breakthroughs.
> `my_profile` is fully open source as part of the `egeria-python` project. Try it out in your own terminal, connect it to the Coco Pharmaceuticals demo environment, and experience how open metadata can transform your working day.
> Thanks for watching, and see you next time!

**[END CARD & RESOURCE LINKS]**
- **Egeria Project:** [https://egeria-project.org](https://egeria-project.org)
- **Coco Pharmaceuticals Personas:** [https://egeria-project.org/practices/coco-pharmaceuticals/personas/](https://egeria-project.org/practices/coco-pharmaceuticals/personas/)
- **PRD Associates & Jules Keeper Video Blogs:** [https://www.prd-associates.com](https://www.prd-associates.com)
- **Egeria Python SDK & TUI:** [https://github.com/odpi/egeria-python](https://github.com/odpi/egeria-python) (`my_egeria` package)
- **Launch Command:** `uv run my_profile` or web interface via `uv run serve_my_profile`
- *"Watch Video Blog 3: Establishing Data Governance by Jules Keeper on YouTube"*

---

## Production & Recording Notes

- **Presenter Persona & Tone:** Callie Quartile (Data Scientist). Warm, authentic, sharp, and collegial. She communicates as a research practitioner sharing practical daily wins with fellow data professionals.
- **Narrative Continuity:** Directly references Jules Keeper's CDO video blogs (specifically Video Blog 3 on *Establishing Data Governance*), illustrating how executive governance principles translate into practitioner tools.
- **Visual Recording Standards:**
  - 1080p (1920×1080) 60fps recording.
  - Large monospace font (≥18pt, e.g. JetBrains Mono) with the official `my_profile.tcss` dark theme.
  - Spotlight zoom on active widgets during keypresses with animated shortcut overlays.
- **Demo Data Pre-Seeding:**
  - Use standard Coco Pharmaceuticals demo environment (user: `calliequartile`, view server configured).
  - Pre-seed active to-dos, comments linking Dr. Tessa Tube, and sample data products in the Digital Product Catalog (e.g. Clinical Trial Cohort metrics).
- **Web-TUI Accessibility Note:** Include a brief 5-second b-roll cutaway showing `serve_my_profile` accessible over standard web browsers via web sockets.
- **Social Media & Video Description Copy:**
  > Meet My Profile! 🚀 The interactive terminal cockpit for Egeria users at Coco Pharmaceuticals. In this practitioner video blog, Data Scientist Callie Quartile demonstrates how she puts Jules Keeper's "better data for everyone" initiative into practice—managing research teams and to-dos, exploring data glossaries, sampling data products, and subscribing to governed datasets in seconds.
  >
  > 📺 Companion to the Jules Keeper Coco Pharmaceuticals Video Series by Mandy Chessell.
  > 🔗 Personas & Architecture: https://egeria-project.org/practices/coco-pharmaceuticals/personas/
  > 🌐 PRD Associates: https://www.prd-associates.com
  > 💻 Open Source Repository: https://github.com/odpi/egeria-python
  > #Egeria #DataGovernance #OpenMetadata #Python #Textual #DataMesh #CocoPharmaceuticals
