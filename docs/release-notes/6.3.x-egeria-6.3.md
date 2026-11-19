# pyegeria 6.3.1, with 6.3.0 and the 6.2 series that led to it

pyegeria 6.3.1 is the Python client for **Egeria 6.3**. This page describes what's new in 6.3.1 and 6.3.0, then the
6.2 series of releases that led up to them.

```bash
pip install -U pyegeria
```

## pyegeria 6.3.1

Released 2026-11-18 ([odpi/egeria-python#603](https://github.com/odpi/egeria-python/pull/603), [release](https://github.com/odpi/egeria-python/releases/tag/v6.3.1)).

### Behaviour changes

- **The library has no built-in password or admin credential.** With no password configured, signing in fails with a
  clear message (`PyegeriaInvalidParameterException`) before any request goes to Egeria, instead of reaching Egeria
  with an empty or guessed password and getting a 401. If your code catches that 401, catch the new exception as
  well. `resolve_egeria_credentials`, the `ADMIN_USER` / `ADMIN_PASSWORD` settings and `UserProfileConfig.user_pwd` no
  longer have built-in values (PY-33, PY-35).
- **The command-line tools keep their demo-password fallback until 6.4**, so set `EGERIA_USER_PASSWORD` now in the
  shell where you run them (never in a server's or container's environment). *Setting your Egeria password*
  (`docs/setting-your-egeria-password.md`) explains where pyegeria looks for it.
- **In a process declared multi-user, a report run with no user is refused** instead of running as the service
  account. This covers Egeria Advisor, Studio and pyegeria's MCP HTTP server. Single-user use, such as the
  command-line tools and notebooks, is unchanged (PY-32).

### Fixes

- `add_like_to_element` sends the emoji you choose and doesn't fix a zone (PY-29).
- Dr.Egeria's MCP `run_block`: a block whose headings are a level off no longer reports "0 commands, success"; it
  gives hints naming the line and the fix (PY-30).
- `delete_collection`'s documentation matches the code: cascade defaults to off (PY-31).
- Report-spec authoring checks `find_authored_elements` against the element type the spec fixes, instead of warning
  that the type is unknown (PY-34).

### Also included

- **My Profile works with communities directly**: resources, joining, and feedback on posts and resources
  ([#601](https://github.com/odpi/egeria-python/pull/601)).
- My Egeria no longer prints voice gender in the episode roster ([#602](https://github.com/odpi/egeria-python/pull/602)).

## pyegeria 6.3.0

Released 2026-11-16 ([odpi/egeria-python#600](https://github.com/odpi/egeria-python/pull/600), [release](https://github.com/odpi/egeria-python/releases/tag/v6.3.0)).

pyegeria 6.3.0 is the release that matches Egeria 6.3. It follows 6.2.42 and adds the changes below. If you're coming
from an earlier 6.2 release, [the 6.2 series](#the-62-series) below describes what led up to it.

### Paging on Egeria 6.3

- **pyegeria now knows which Egeria fixes a platform carries**, one version check per upstream fix, and trusts a read
  only on a platform that has every fix it needs (`pyegeria.core.paging`, `platform_fixes`). Egeria 6.3 carries
  both paging fixes: odpi/egeria#9453, for the find reads, and odpi/egeria#9454, for `get_relationships` and
  `get_related_elements`. Released Egeria from 6.3.0 on is trusted for both, since the V6.3 tag carries both fixes.
  On Egeria 6.3, pyegeria can tell when it has read to the end of those results. On older platforms, counts are
  reported as "at least N".
- **Data-asset searches filter on content status.** `find_data_assets` and `get_data_assets_by_category` return only
  assets whose content status is ACTIVE by default. Assets with no content status, such as many catalogued by
  integration connectors, are left out; pass `content_status_list=[]` to get them all. Like every read, they return
  only what the caller can see.
- **A find's count says "at least N" unless the end was confirmed.** `result_count(result)`
  (`pyegeria.view.format_set_executor`) gives the count, its wording, and the reason when it isn't final.
- **MCP report runs page up to their maximum rows** and include a count, so a filtered first page no longer reads as
  "nothing".

### Dr.Egeria and authoring

- **Limit Result by Status** is a list of element statuses, with lifecycle filters added.
- **Project Scope** maps to the project's `scope` property.
- **Default value overrides** are sent when the target type declares them.
- **Authoring validation is stricter**: the find method must suit the target type, and column keys are checked.
- **Deployment status matches Egeria** (PY-21). The fallback list of deployment statuses offered
  `REJECTED_FOR_DEPLOYMENT`; Egeria's value is `REJECTED`.
- **Drafts are listed correctly on a live Egeria.** Listing and pruning drafts used to find none on a real server.
  They now read each kind by type, filtered by the author's zone.
- **Egeria 6.3's type system**: the properties catalog is regenerated from Egeria, and the `queries` attribute is no
  longer sent or accepted on schema types.

### Planned for pyegeria 6.4 or the next release

- **`load_egeria_report_specs` will be removed in pyegeria 6.4 or the next release.** It has been deprecated since 6.2.42 (#598) and
  logs a warning once. Report specs held in Egeria load through the spec cache (`pyegeria.view.egeria_spec_cache.sync_report_specs`).
- **Set `EGERIA_USER_PASSWORD` now.** pyegeria's command-line tools (`hey_egeria` and the other CLIs) still fall
  back to the QuickStart demo password when `EGERIA_USER_PASSWORD` isn't set. pyegeria 6.4 removes that fallback, so
  set `EGERIA_USER_PASSWORD` now in the shell where you run the command-line tools (never in a server's or container's
  environment).
- **pyegeria 6.4 or the next release drops the default password** and any built-in identity, except in a demo profile
  that is named explicitly.

## The 6.2 series

We released pyegeria 42 times between 6.2.0 (October 8, 2026) and 6.2.42 (November 15, 2026), about four releases a
week. (6.2.38 was tagged but not published to PyPI; 6.2.39 includes its fixes.) Together with 6.3.0 and 6.3.1 they make up the
Python side of **Egeria 6.3**. This page groups the releases by theme, so you can see what changed without reading each one. The per-release notes from 6.2.26 onwards are in this folder; earlier releases are
described in their release PRs.

**If you are upgrading from 6.2.0, read [Behaviour changes](#behaviour-changes) first.**

### The last three: 6.2.40 to 6.2.42

These three releases, from November 12 to 15, came just before 6.3.0.

**6.2.40: Dr.Egeria writes what you asked for** (#593)
- Every property of every Dr.Egeria Create command was written to a test Egeria and read back, and this release
  fixes what didn't come back. Search Keywords are now attached, glossary-term flags become the matching
  classifications, and schema attribute positions and cardinality go on the link to the parent.
- **An attribute Dr.Egeria can't send is reported, not dropped.** The command's warnings say
  `not applied: <attribute>: <reason>`.
- Commands Dr.Egeria can't carry out say why and send nothing, and every failure prints its exception and Egeria's
  message id on one line. Several Create commands that used to fail now run.
- `pyegeria.view.report_spec_publish` builds and checks the Dr.Egeria documents that publish and withdraw report
  specs, so the Portal and Egeria Advisor do it the same way.
- See [6.2.40](6.2.40.md) for the details and the known issues, including that Egeria replaces
  `additionalProperties` as a whole map.

**6.2.41: the authoring API** (#595)
- **`pyegeria.authoring`** for report specs, Reports and dashboard sheets: drafts, validation, preview as a given user,
  diff and publish, with MCP tools. Drafts are private to their author and are pruned after 30 days.
- **Published versions don't change.** Each publish records its version, time and publisher, and an update is refused
  unless its exact target can be found.
- **`additionalProperties` is merged key by key on update**, so re-importing a spec no longer drops keys.
- **The MetadataExpert commands** in Dr.Egeria (16 of them) work on type and enum definitions and raw elements.
  They aren't allowed from chat, and the destructive ones need the GUID or name typed back before anything is written.

**6.2.42: paging that doesn't stop early, and no password you didn't give** (#598)
- **Paging:** every loop that pages goes through `pyegeria.core.paging`, and a short or empty page isn't taken as the
  end. A lookup answers found, absent or unknown; an error is never "absent".
- **No password you didn't give:** pass `user_pwd=NO_PASSWORD` to hold no password, typically with a bearer token.
  A client pyegeria builds for another client gets that client's token and never the configured default password.
  `user_pwd=None` still takes the configured password, as before.
- **Report specs are cached per user**, which fixes a race where one user's request could get another user's specs.
  A server that acts for many users can say so (`PYEGERIA_MULTI_USER=1`), and then gets no fallback identity.
- **Authoring:** `can_edit` (yes, no or unknown) and `used_by` (what uses this spec, Report or sheet), both read as
  the user; a refusal carries an `answer` of absent, unknown or refused.
- `egeria-table.js`, the table renderer the Portal and Egeria Advisor share, ships with the package.
- `load_egeria_report_specs` is deprecated; see *Planned for pyegeria 6.4 or the next release* above.

### Report specs and analytic functions

- **Found by registered name.** Analytic functions resolve by registry name or an allowed module prefix (#516), can
  carry a declaration (#517), say why a result is absent instead of returning it as data (#518), and are discovered
  from installed packages (#519). Report specs are found by registered name, with `pyegeria.report_specs` entry points
  (6.2.18, #523).
- **Every routine declares itself** (6.2.24, #539) and a routine's declaration and bindings are first-class, with
  `AnalyticFunctionSpec` as a view of them (#546).
- **Every report spec is resolved when it loads**; specs that cannot run are listed with the reason
  (6.2.25, #548). The executor supplies declared inputs by role (6.2.26, #552), and the old analytic binder is removed
  (#553). See [Routines, declarations and roles](../output-formats-and-report-specs.md#routines-declarations-and-roles).
- **Report specs held in Egeria**, run from plain pyegeria (6.2.28, #563, #564, #569); specs are organised in consumer
  folders with a recursive sync and consumer index (6.2.33, #582); restricted specs (6.2.35, #587).
- **Search and get filters** are universal, checked and typed (6.2.28, #567).
- **Standard documents and complex values** (6.2.37, #589): a DOCUMENT output type with validators that never fetch
  over the network, and a built-in **DCAT Catalog** spec that exports a collection's Assets as a DCAT-AP 3 catalog,
  validated against the shipped SHACL shapes; an opt-in structured TABLE (`table_shape="structured"`) and native DICT
  (`dict_shape="native"`), with per-column render intents. Existing calls return the same shapes. The DCAT Catalog
  runs with a search string as well as a scope (6.2.38, #590). See
  [Output formats and report specs](../output-formats-and-report-specs.md) (#592).

### Dashboards and measurements (Egeria 6.3)

- **Client and Dr.Egeria commands** for Egeria 6.3 report specs, measurements and dashboards (6.2.24, #540, #541).
- **Dashboard sheets** are written as Egeria 6.3 Dashboard elements (#570), read from Egeria (#571), held with an
  owner (6.2.31, #578), and organised in Egeria folders, with a sheet's spec fetched as the viewer (#586).
- **Collection Members by qualifiedName**, `saved_query` reports, exact trend points and the Saved Query Formula
  (6.2.34, #585); Saved Query delete, Smart Collections by catalog target, and report parameters on dashboard Reports
  (6.2.35, #587).

### Overview metrics: measured or not measured

- **A value that wasn't measured is `None`, not 0** (6.2.22, #531; opt-in strict counts since #448). A count that hit
  its cap or timed out is reported as not measured, rather than as the cap (#555); scans either read every page or
  report nothing (#565).
- **`asset_composition`**, with a subtype tree and two count scopes (6.2.23, #534); the absence word `nothing_found`
  (#535).
- **`population=`** is the count keyword; `scope=` is deprecated (6.2.24, #538).
- **Totals count the whole repository** by default (6.2.27, #556); `stale_assets` counted by update-time bisection (#572).

### Dr.Egeria

- **Reference Data** authoring, and the Valid Metadata family split (6.2.3, #449).
- **Credentials resolved at run time** with one precedence chain (#477); Postgres commands take a secrets store (#478).
- **Updates no longer reset properties the document doesn't set** (6.2.10, #482).
- **New commands**: Business Capability, Business Capability Dependency and Digital Support (6.2.11, #486); statements
  of applicability (#492, #493); survey reports and security findings (#497).
- **Link and detach commands that reported success but sent nothing** are fixed (6.2.28, #566).
- **Zone Membership in Basic templates**; blank zones are no longer cleared (6.2.30, #577).
- **Parent ID keeps memberships**, templates ship as package data, and a dashboard resolver (6.2.32, #581).
- **A bullet in a list attribute is one item**, commas and all (6.2.39, #591). Write list values as bullets.

### Egeria 6.3 compatibility

- Governance Engine client for the engine-action operations Egeria moved (6.2.5, #460).
- Boxed properties, and a failed bearer-token request now raises (6.2.13, #498).
- Information supply chain mermaid graphs (6.2.14, #503); every Egeria graph key, with action and activity graphs
  beside the context graph (6.2.29, #573).
- Lineage graph `maxHops` and `skipRelationships` (#526).
- Configurable TLS verification of the platform certificate (#530).
- Endpoints Egeria removed are routed to their replacements and deprecated (#485); `get_platform_organization` reads
  `/api/public/app/info` (6.2.11, #487).
- `NotificationType` drops `notificationInterval`; subscription types use `minimumNotificationInterval` (#558).
- Security annotation models and findings/posture reports (#495).

### My Egeria (formerly My Profile)

- One key-binding convention and a discoverable My Team view (#463, #469); My Network option (#458).
- Renamed to `my_egeria.py` (6.2.12, #491); login as a different user and no-Egeria startup handling (#501, #507).
- Edit Profile saves to Egeria (#524).
- Promoted to a production package (#580), with a recorded video blog and voiceover pipeline (#584).
- Selecting a business domain passes the GUID (6.2.38, #590).

### Correctness

- Five update methods that sent no body (6.2.7, #471).
- Request fields silently dropped SDK-wide (6.2.10, #483).
- By-name wrappers: the type filter reaches Egeria, and a body-only call is accepted (#439, #445).
- Template builders gained the placeholders Egeria added (#474, #475).
- Link methods return relationship GUIDs; Pydantic V2 (6.2.19, #525). Five link methods named a properties class
  Egeria lacks (#537).
- A caller-supplied token is not re-authenticated as the client's user (6.2.15, #508).
- **Runs without `nest_asyncio`, so pyegeria works on Python 3.14** (6.2.16, #513).
- `get_collection_members` pages; folder walks page every folder; no paging loop can run forever (6.2.36, #588,
  ISSUE-185).

### Security

- certifi floor excluding the distrusted emSign G3 root, and tornado 6.6 (6.2.21, #529).
- The MCP server signs in as the configured identity rather than a built-in one, and the unique-name lookup no longer
  signs in with the default password (6.2.42, #598).
- One user's report specs can no longer be served to another user's concurrent request (6.2.42, #598).

### Behaviour changes

| Since | Change | What to do |
|---|---|---|
| 6.2.13 | A failed bearer-token request raises instead of returning quietly (#498). | Catch the exception where you handled an empty token. |
| 6.2.19 | Link methods return the relationship GUID (#525). | Use the return value if you need the relationship. |
| 6.2.22 | Unmeasured overview counts are `None`, not 0 (#531). | Treat `None` as "not measured"; don't add it as 0. |
| 6.2.23 | Absence word `nothing_found`; the legacy `measured_nothing` is still read (#535). | Write `nothing_found`. |
| 6.2.24 | `population=` replaces `scope=` on overview counts; `scope=` is deprecated (#538). | Rename the keyword. |
| 6.2.26 | The analytic binder is removed; inputs are supplied by role (#552, #553). A spec that still carries `analytic_binders` warns (#561). | Declare `inputs` on the routine. |
| 6.2.27 | Totals count the whole repository by default (#556). | Expect larger totals. |
| 6.2.34 | An element hidden by zone security is reported as `AUTHORIZATION_ERROR_403`, not `_401`; the exception class is unchanged and a 403 is never retried (#585, ISSUE-182). | If you match `AUTHORIZATION_ERROR_401` in the text, match `AUTHORIZATION_ERROR` instead. |
| 6.2.36 | With `body=` and no paging in the body, the method's `page_size` default now applies on 19 methods (#588). | Put `pageSize` in the body, or pass `page_size`, if you relied on Egeria's default page. See [6.2.36](6.2.36.md). |
| 6.2.37 | Rendered **text** changes (REPORT, LIST, MD, FORM, HTML, the CLI table): LIST cells are drawn by what the value is, and capped results say "more may exist" (#589). Result shapes are unchanged. | Re-check anything that parses pyegeria's rendered text; read DICT or JSON instead. See [6.2.37](6.2.37.md). |
| 6.2.39 | Dr.Egeria: a single bullet on its own line, such as "- a, b", is one item (it used to be two) (#591). | Write one item per bullet. See [6.2.39](6.2.39.md). |
| 6.2.40 | Dr.Egeria reports attributes it can't send (`not applied: …`) and no longer sends keys the Egeria type doesn't declare (#593). | Read the warnings; fix or remove the attributes they name. See [6.2.40](6.2.40.md). |
| 6.2.41 | An update merges `additionalProperties` key by key (#595). | Nothing, unless you relied on an update removing keys. |
| 6.2.42 | The report-spec cache takes its default identity from the process's own client, not the shell's `EGERIA_USER` (#598). | Pass the client, or set the identity explicitly, if you relied on `EGERIA_USER`. |

### Dependencies and housekeeping

- multidict 6.9.1 (#437); codeql-action and action-gh-release bumps (#441, #442, #559, #560); consolidated Dependabot
  updates (#502).
- The issue trackers (`PYEGERIA_ISSUES.md`, `EGERIA_OPEN_ISSUES.md`) were re-derived and kept current through the
  Egeria re-test passes.

### Release-by-release

| Version | Date | Release PR |
|---|---|---|
| 6.2.1 – 6.2.10 | Oct 10 – Oct 23 | #443, #447, #455, #459, #461, #467, #473, #476, #479, #484 |
| 6.2.11 – 6.2.20 | Oct 24 – Nov 3 | #487, #494, #499, #504, #511, #515, #522, #523, #525, #527 |
| 6.2.21 – 6.2.30 | Nov 4 – Nov 10 | #529, #533, #536, #545, #551, #554, #557, #568, #575, #577 |
| 6.2.31 – 6.2.39 | Nov 10 – Nov 12 | #578, #581, #583, #585, #587, #588, #589, #590, #591 |
| 6.2.40 – 6.2.42 | Nov 12 – Nov 15 | #593, #595, #598 |
| 6.3.0 | Nov 16 | #600 |
| 6.3.1 | Nov 18 | #603 |

Detailed notes: [6.2.26](6.2.26.md) · [6.2.27](6.2.27.md) · [6.2.28](6.2.28.md) · [6.2.29](6.2.29.md) ·
[6.2.30](6.2.30.md) · [6.2.31](6.2.31.md) · [6.2.32](6.2.32.md) · [6.2.33](6.2.33.md) · [6.2.34](6.2.34.md) ·
[6.2.35](6.2.35.md) · [6.2.36](6.2.36.md) · [6.2.37](6.2.37.md) · [6.2.38](6.2.38.md) · [6.2.39](6.2.39.md) · [6.2.40](6.2.40.md)
