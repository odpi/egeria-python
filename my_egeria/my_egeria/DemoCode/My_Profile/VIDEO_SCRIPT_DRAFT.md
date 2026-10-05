# My Profile — Video Blog Script (DRAFT)

**Working title:** "Meeting Egeria Through My Profile — Callie Quartile, Data Scientist at Coco Pharmaceuticals — Video Blog"
**Target length:** ~4 minutes (≈550 spoken words)
**Format:** In-character video blog set at Coco Pharmaceuticals, in the same style as the Jules Keeper series. Talking head / voice-over, cutting to screen capture of `my_profile_app.py` running in a terminal.
**Presenter persona:** Callie Quartile, data scientist at Coco Pharmaceuticals (swap in another Coco persona if you prefer; see the notes at the end).

---

## 0. Cold open (0:00 – 0:15)

**[VISUAL]** Presenter to camera, or a Coco Pharmaceuticals title card: *"Better data for everyone"*.

**CALLIE:**
> Hi, I'm Callie Quartile. I'm a data scientist at Coco Pharmaceuticals. When Jules Keeper, our Chief Data Officer, launched *"better data for everyone"*, my first question was pretty simple: where do I actually start? It turns out I start with **me**.

---

## 1. The problem (0:15 – 0:40)

**[VISUAL]** Simple slide: a person in the middle, with icons around them for teams, roles, projects, data, and to-dos. Lines connect them.

**CALLIE:**
> Egeria already knows a lot about me: which teams I'm on, the roles I hold, my projects, the data I use. But that knowledge is spread across the metadata. I wanted one place where I could see it, keep it up to date, and act on it. That place is **My Profile**.

---

## 2. Launch and splash screen (0:40 – 1:00)

**[VISUAL]** Terminal. Type `python my_profile_app.py`. The splash screen appears with *"Welcome to My_Profile for Egeria Users, callie!"* and the **Continue to App** / **Change User** buttons.

**CALLIE:**
> My Profile is a terminal app built on pyegeria. While this welcome screen is showing, it's already loading my profile from Egeria in the background, so by the time I press Continue it's ready.
> If I'm sharing a desk, or testing as a colleague, **Change User** lets me sign in as someone else. Egeria checks the credentials before letting me through.

**[ON-SCREEN CALLOUT]** "Profile loads in parallel with the splash screen"

**[OPTIONAL CUTAWAY]** If a user has no profile yet, the app offers the **Create Profile** form (courtesy title, job title, and so on).

---

## 3. The main dashboard (1:00 – 1:45)

**[VISUAL]** Main screen. Slowly pan or highlight each panel as it's mentioned. The header shows "Egeria — My Profile" and the clock.

**CALLIE:**
> This is my home screen. Everything here comes live from Egeria.
> Up here are my **associations** and my **collections**. Next are the **roles** I've been appointed to and the **teams** I belong to.
> This panel is my working life: my **blog**, my **journal**, and my **to-dos**.
> Down here is my **user identity**, which is how Egeria recognises me across the tools I use.

**[ON-SCREEN CALLOUT]** Point out the keyboard shortcuts in the footer: `Ctrl+T` Edit, `Ctrl+S` Comments, `Ctrl+B` Bookmarks.

---

## 4. Keeping it current (1:45 – 2:20)

**[VISUAL]** Select the To-Dos table, press `Ctrl+T`, and add a to-do: *"Review clinical trial data quality report"*. Back on the main screen the new row appears. Then highlight a row and press `Ctrl+S` to show and add a comment.

**CALLIE:**
> The profile is only useful if it's accurate. I pick any table and press **Ctrl+T** to edit it: add a row, update one, or remove something that's no longer true. Here I'm adding a to-do from this morning's stand-up.
> **Ctrl+S** opens the comments on whatever row I've selected, so a conversation stays attached to the thing it's about, not lost in email.

**[OPTIONAL]** Quick shot of **Edit Profile** from the Other Functions list, updating the job title.

---

## 5. Shopping for data (2:20 – 3:05)  ← *the "hero" moment*

**[VISUAL]** Other Functions → **Catalogs / Shop for Data**. Show the Glossary, Digital Product Catalog, Data Dictionary, Business Domain, and Root Collection panels. Select a data product, press `s` to **sample** it, then `u` to **subscribe**. Fill in the subscription request and submit. Then open **Subscriptions** to show it listed.

**CALLIE:**
> This is the part I use most. **Shop for Data** brings together our glossary, the digital product catalog, data dictionaries, and business domains in one place.
> I can find the product I need and **sample** it before I commit. When it's right, I **subscribe**. That sends a proper subscription request through Egeria, so the data owner knows who's using their data and why.
> And under **Subscriptions** I can see everything I've signed up for.

**[ON-SCREEN CALLOUT]** "Governed access, requested in seconds"

---

## 6. Bookmarks and technology types (3:05 – 3:30)

**[VISUAL]** Press `Ctrl+B` to show the bookmarks list and add one. Then Other Functions → **Technology Types**. Pick a technology type and show its templates and processes.

**CALLIE:**
> **Ctrl+B** keeps my bookmarks, the elements I come back to again and again.
> And for the more technical among us, **Technology Types** shows what Egeria knows about each technology, including the templates and processes it can run for you.

---

## 7. Close and call to action (3:30 – 4:00)

**[VISUAL]** Back to presenter, or the main dashboard. End card with links.

**CALLIE:**
> So that's My Profile: one place to see how I fit into Coco Pharmaceuticals, keep it accurate, and get the data I need, with governance built in rather than bolted on.
> Better data for everyone really does start with everyone. Next time, I'll show how my team uses this to share projects and to-dos.
> The app is open source, part of the Egeria Python project. Links are below. Give it a try against the Coco Pharmaceuticals demo environment.

**[END CARD]**
- Egeria project: https://egeria-project.org
- egeria-python on GitHub (link to `my_egeria/DemoCode/My_Profile`)
- "Previous in series: Jules Keeper video blogs" (link to the playlist)

---

## Production notes

- **Presenter persona:** Callie Quartile was chosen because Shop for Data and Subscribe fit a data scientist's day. Other Coco personas that would work: Peter Profile (information specialist, and a natural fit for "My Profile"), Tessa Tube (lead researcher), or Jules Keeper as a cameo in the opening. Check the names and roles against the current Coco Pharmaceuticals docs.
- **Tone:** first person, warm, practical, a little wry. It's one colleague showing another, not a feature tour. Each feature should be tied to a job Callie actually needs to get done.
- **Screen capture:** use a large terminal font (≥18pt) and a dark theme matching `my_profile.tcss`. Record at 1920×1080 and zoom in on the panel being discussed. Pause about half a second before each keypress so viewers can follow.
- **Demo data:** record against the Coco Pharmaceuticals demo data, so the teams, roles, and data products shown match the rest of the series. Pre-create a few to-dos, blog and journal entries, and one subscribable data product.
- **Captions:** burn in the keyboard shortcuts (`Ctrl+T`, `Ctrl+S`, `Ctrl+B`, `s`, `u`) as they're used.
- **Before recording:** check every step against the current build, especially Change User, Create Profile, and Subscribe, since they've changed recently.
- **LinkedIn post (draft):**
  > Meet My Profile 👋 A terminal app for Egeria users that shows your teams, roles, projects, and to-dos in one place, and lets you shop for governed data and subscribe to it in a few keystrokes. Watch Callie Quartile from Coco Pharmaceuticals take it for a spin: [YouTube link] #Egeria #OpenMetadata #DataGovernance #LFAIData
