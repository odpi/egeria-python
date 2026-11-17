# Coco Pharmaceuticals Business Value Video Series — Production Scripts & Cue Sheets

**Series Context:** *Coco Pharmaceuticals Data Governance Journey*  
**Executive Sponsor:** Jules Keeper (Chief Data Officer) & Reggie Mint (Chief Financial Officer)  
**Practitioner Anchor:** Companion to Mandy Chessell's Jules Keeper Video Series ([prd-associates.com](https://www.prd-associates.com)) and Egeria Technical Blog Series (Parts 6–10).  
**Format:** 1080p Full HD video blog episodes combining presenter dialogue, Catppuccin Mocha title cards/slide decks, and automated terminal recordings (`my_profile.py`).  
**Voice Synthesis:** Microsoft Azure Neural TTS (`edge-tts`) with distinct regional accents per persona, plus offline macOS `say` support.

---

## Technical Blog Mappings (Egeria 6.3 Release & Architecture)

Each episode connects directly to the architectural patterns and technical features detailed in Mandy Chessell's latest technical blog series ([Egeria Docs Blogs](https://github.com/odpi/egeria-docs/tree/main/blogs)):

| Episode | Lead Persona | Topic | Primary Technical Blog References |
|:---|:---|:---|:---|
| **Episode 0** | **Callie Quartile** | Practitioner Cockpit & Shopping for Data | **Blog 6** (Autonomous Housekeeping & Karma), **Blog 8** (Bitol ODCS Contracts), **Blog 10** (DCAT v3 Exchange) |
| **Episode 1** | **Faith Broker** | Automating Data Privacy & GDPR Compliance | **Blog 7** (NIST CSF 2.0 / SP 800-53 OSCAL Catalogs, ISO 27001 SoA, Fail-Closed Security Zones) |
| **Episode 2** | **Peter Profile** | Zero-Touch Stewardship & Curation at Scale | **Blog 6** (Automated Connectors: `Simon`, `Pasteur`, `Mendel`; Reversible `Undo` / `Restore`) |
| **Episode 3** | **Dr. Tessa Tube** | Clinical Data Provenance & Trial Integrity | **Blog 8** (Bitol ODCS/ODPS, `Darwin` Dependency Validation) & **Blog 9** (5 Lineage Layers) |
| **Episode 4** | **Stew Faster** | Supply Chain Traceability & ESG Sustainability | **Blog 10** (W3C DCAT v3 JSON-LD Document Exchange & Connectors: Files, Events, Publishers) |
| **Episode 5** | **Erin Overview** | Business Glossaries & Technical Architecture | **Blog 9** (PostgreSQL-backed OpenLineage graph analysis, 5 Lineage Layers, Bounded Exploration) |
| **Episode 6** | **Sidney Seeker** | Forensic Auditing & Fraud Investigation | **Blog 6** (Reversible Operations) & **Blog 7** (STRIDE Threat Models, Tamper-Evident History) |
| **Episode 7** | **Jules Keeper & Reggie Mint** | Executive Cockpit: Measuring Data ROI | **Blog 6** (TCO Reduction & Autonomous Housekeeping), **Blog 7** (Security Posture), **Blog 8** (Data Mesh ROI) |

---

## Episode 1: Automating Data Privacy & GDPR Compliance

* **Lead Persona:** Faith Broker (`faithbroker`) — HR Director & Data Privacy Officer
* **Voice Profile:** `en-GB-LibbyNeural` (British English, Authoritative & Professional)
* **Business Driver:** Regulatory Compliance (GDPR, HIPAA), Privacy Governance & Risk Mitigation
* **Target Audience:** Data Privacy Officers, Compliance Directors, Legal Counsel, HR Executives

### Scene Breakdown & Teleprompter Cue Sheet

#### Scene 0: Cold Open — The Compliance Challenge
* **Speaker:** Faith Broker
* **Visual:** Slide Card — Title: *EPISODE 1: AUTOMATING DATA PRIVACY & GDPR*
* **Callouts:**
  - Challenge: Manual Subject Access Requests (SARs) take weeks of manual investigation
  - Risk: GDPR & HIPAA non-compliance penalties and clinical patient exposure
  - Egeria Solution: Automated classification tagging and unified metadata lineage
  - Security Frameworks: NIST CSF 2.0 & ISO 27001 Statement of Applicability
* **Dialogue:**
  > "Hello, I'm Faith Broker, HR Director and Data Privacy Officer at Coco Pharmaceuticals. When GDPR, HIPAA, and patient privacy regulations require you to locate, classify, and protect every piece of personally identifiable information across hundreds of clinical and employee databases, traditional manual audits simply cannot keep up. Today, I'm going to show you how open metadata with Egeria turns privacy compliance from a terrifying manual bottleneck into an automated, continuous operational safeguard."

#### Scene 1: The Governance Context — Privacy Classifications
* **Speaker:** Faith Broker
* **Visual:** Slide Card — Title: *GOVERNANCE CLASSIFICATIONS & PRIVACY CONTROLS*
* **Callouts:**
  - Security Content Pack: Built-in NIST CSF 2.0 and NIST SP 800-53 OSCAL catalogs
  - Standardized Classifications: Confidentiality, Impact, Criticality, Retention
  - Fail-Closed Security Zones: Operational metadata restricted by default
  - ISO 27001 Mapping: Statement of Applicability directly linked to data assets
* **Dialogue:**
  > "In our corporate governance council, Chief Data Officer Jules Keeper and I established clear governance classifications. Egeria integrates pre-packaged NIST CSF 2.0 and SP 800-53 security controls, aligning directly with our ISO 27001 Statement of Applicability. Every asset entering our data estate is automatically evaluated for Confidentiality, Impact, and Retention within fail-closed security zones. In my workspace, I can instantly see which clinical trial cohorts contain restricted patient identifiers, and ensure that governance action engines enforce masking policies before research data is ever shared."

#### Scene 2: Workspace Navigation — Privacy Role & Team Hierarchy
* **Speaker:** Faith Broker
* **Visual:** Terminal — `uv run my_profile --user faithbroker` (Roles & My Team drill-down)
* **Dialogue:**
  > "Let's step into the My Profile workspace. Logging in as Faith Broker, the system immediately loads my assigned governance roles. Notice my association with the Corporate Privacy Council and HR Leadership team. I can drill down into my team hierarchy, verifying that Tanya Tidie in Clinical Records and our data stewards have completed their privacy review to-dos for the newest clinical hospital feeds."

#### Scene 3: Subject Access Request (SAR) & PII Lineage
* **Speaker:** Faith Broker
* **Visual:** Terminal — Shop for Data & My Network graph filtering for Restricted PII
* **Dialogue:**
  > "When an employee or clinical trial participant submits a Subject Access Request, we no longer need to email dozens of database administrators. Using the unified catalog search and My Network graph, I can trace the entire information supply chain for patient identifiers. From raw ingestion tables in PostgreSQL to S3 data lakes and analytics marts, Egeria maps the full lineage and confidential relationships in seconds."

#### Scene 4: Real-Time Privacy Stewardship & Feedback
* **Speaker:** Faith Broker
* **Visual:** Terminal — To-Dos panel, `Ctrl+N` for audit comment, `Ctrl+F` for feedback modal
* **Dialogue:**
  > "If a new dataset lacks appropriate retention rules, I can immediately tag a to-do, add an audit comment with Control-N, or submit real-time feedback with Control-F directly to the engineering team. Our data stewards earn Karma Points for completing privacy validations, making compliance a collaborative, rewarding process."

#### Scene 5: Business Impact & Executive Takeaways
* **Speaker:** Faith Broker
* **Visual:** Slide Card — Title: *BUSINESS IMPACT & EXECUTIVE ROI*
* **Callouts:**
  - 95% Reduction in SAR Response Time: From 3 weeks to under 2 hours
  - Zero-Defect Audit Readiness: Continuous automated metadata classification
  - Fail-Closed Protection: Operational secrets and PII strictly isolated
  - Explore Egeria: egeria-project.org • Egeria Security Blog Series Part 7
* **Dialogue:**
  > "By anchoring privacy governance in Egeria's open metadata ecosystem, Coco Pharmaceuticals reduced Subject Access Request response times from three weeks down to under two hours, while eliminating the risk of regulatory fines. Data privacy is no longer a barrier to research—it's the trusted foundation that enables our scientists to innovate with confidence. Thank you for joining me!"

---

## Episode 2: Zero-Touch Data Stewardship & Curation at Scale

* **Lead Persona:** Peter Profile (`peterprofile`) — Information Analyst & Lead Data Steward
* **Voice Profile:** `en-GB-RyanNeural` (British English, Engaging & Methodical)
* **Business Driver:** Data Quality, Semantic Consistency & Curation Productivity
* **Target Audience:** Data Stewards, Information Analysts, Data Governance Teams, Analytics Engineers

### Key Technical Mechanisms (Blog 6)
- **Housekeeping Connectors:** `Simon` (Karma calculation), `Pasteur` (task/process archival), `Mendel` (tag deduplication).
- **Native Reversibility:** Full `Undo` and cascading `Restore` for schemas, tables, and relationships.

---

## Episode 3: Trusted Clinical Data Provenance & Trial Integrity

* **Lead Persona:** Dr. Tessa Tube (`tessatube`) — Lead Clinical Researcher
* **Voice Profile:** `en-US-AriaNeural` (American English, Academic & Authoritative)
* **Business Driver:** Scientific Integrity, Regulatory Filings (FDA/EMA), Audit Provenance
* **Target Audience:** Clinical Researchers, R&D Directors, Biostatisticians, Regulatory Affairs

### Key Technical Mechanisms (Blogs 8 & 9)
- **Data Mesh & Contracts:** Bitol Open Data Contract Standard (ODCS) and Open Data Product Standard (ODPS).
- **Darwin Governance Engine:** Validates runtime pipeline lineage events against declared contracts, alerting on unmapped dependencies.
- **Five Lineage Layers:** Business Flow, Data Mesh, System Fabric, Data Fabric, Data Mapping.
- **Differential Delivery:** `Baudot` & `Wedgwood` connectors provision delta updates without event storming.

---

## Episode 4: Supply Chain Traceability & ESG Sustainability

* **Lead Persona:** Stew Faster (`stewfaster`) — Manufacturing General Manager
* **Voice Profile:** `en-AU-WilliamMultilingualNeural` (Australian English, Direct & Pragmatic)
* **Business Driver:** ESG Compliance, Operational Efficiency, Carbon Accounting, IoT Telemetry
* **Target Audience:** COOs, Supply Chain Executives, Sustainability Officers, IoT Engineers

### Key Technical Mechanisms (Blog 10)
- **W3C DCAT v3 Standards:** Bidirectional exchange using JSON-LD across Catalogs, Datasets, Distributions, and DataServices.
- **Connectors:** `DCAT Files Receiver`, `DCAT Event Receiver`, `DCAT Cataloguer`, and `DCAT Publisher`.
- **Industrial IoT:** Connecting MQTT/Kafka sensor telemetry and SCADA gateways to enterprise ESG ledgers.

---

## Episode 5: Connecting Business Glossaries to Technical Architecture

* **Lead Persona:** Erin Overview (`erinoverview`) — Enterprise Information Architect
* **Voice Profile:** `en-US-JennyNeural` (American English, Clear & Visionary)
* **Business Driver:** Semantic Interoperability, Architecture Governance, Vendor Neutrality
* **Target Audience:** Enterprise Architects, Chief Architects, Data Modelers, Integration Engineers

### Key Technical Mechanisms (Blog 9)
- **High-Speed OpenLineage in PostgreSQL:** Analyzing 864,000 events in ~3 seconds (vs. 19 minutes previously).
- **Bounded Graph Exploration:** Default 8-hop radius queries preventing client/terminal freezes.
- **Semantic Federation:** Mapping `ISA` and `HASA` relationships across heterogeneous storage stacks.

---

## Episode 6: Forensic Data Auditing & Fraud Investigation

* **Lead Persona:** Sidney Seeker (`sidneyseeker`) — Lead Fraud Investigator & Security Auditor
* **Voice Profile:** `en-IE-ConnorNeural` (Irish English, Sharp & Methodical)
* **Business Driver:** Fraud Detection, Security Compliance, Shadow IT Discovery, Audit Defense
* **Target Audience:** Internal Auditors, CISOs, Fraud Investigators, Security Analysts, Risk Officers

### Key Technical Mechanisms (Blogs 6 & 7)
- **STRIDE Threat Models:** Built-in threat definitions (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- **Tamper-Evident Lineage:** Timestamped audit trails with author attribution.
- **Reversible Forensics:** Instant `Restore` for maliciously deleted or corrupted schemas and relationships.

---

## Episode 7: The Executive Cockpit: Measuring Data ROI & Strategy

* **Lead Personas:** Jules Keeper (`juleskeeper` - CDO) & Reggie Mint (`reggiemint` - CFO)
* **Voice Profiles:** `en-GB-ThomasNeural` (Jules Keeper) & `en-US-GuyNeural` (Reggie Mint)
* **Business Driver:** Data Valuation, Executive ROI, Strategic Governance, Board Reporting
* **Target Audience:** CDOs, CFOs, CIOs, CEOs, Board Directors, Enterprise Leaders

### Key Technical Mechanisms (Blogs 6, 7, 8)
- **Autonomous Housekeeping ROI:** Operational cost reduction via automated metadata cleanup.
- **Contract Adherence:** Enterprise-wide metrics on Bitol data product subscriptions and SLA compliance.
- **Bottom-Line Financial Impact:** Eliminating duplicate catalog tools and saving 75% discovery time across hundreds of analysts.

---

## Video Distribution & Archival (Shared `pdr-vault`)

All certified 1080p MP4 masters, neural audio tracks, slide PNGs, and manifests are exported to the shared `pdr-vault` directory:
- **Master Videos:** `videos/`
- **Audio Tracks:** `audio/`
- **Slide Graphics:** `slides/`
- **Manifest:** `vault_manifest.json` & `README.md`

### CLI Commands
```bash
# Generate all episodes with automated vault export
./my_egeria/my_egeria/recording/run_series.sh --all --export-vault

# Sync standalone
uv run python my_egeria/my_egeria/recording/export_vault.py --all-assets
```
