"""
Egeria Coco Pharmaceuticals Business Value Video Series - Episode Specifications.

Defines the complete narrative scripts, scene breakdowns, UI cues, and persona
voice/accent profiles for the 7 business value video episodes.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class SceneSpec:
    number: int
    title: str
    speaker: str
    voice: str  # Edge TTS voice ID
    dialogue: str
    slide_title: Optional[str] = None
    slide_subtitle: Optional[str] = None
    callouts: Optional[List[str]] = None
    terminal_cue: Optional[str] = None
    duration_estimate: float = 25.0


@dataclass
class EpisodeSpec:
    id: str
    episode_number: int
    title: str
    subtitle: str
    lead_persona: str
    persona_username: str
    persona_role: str
    persona_team: str
    business_driver: str
    target_audience: str
    voice_name: str
    voice_locale: str
    voice_gender: str
    voice_accent: str
    voice_description: str
    offline_say_voice: str
    scenes: List[SceneSpec] = field(default_factory=list)


# ==============================================================================
# EPISODE ROSTER & SPECIFICATIONS
# ==============================================================================

EPISODES: Dict[str, EpisodeSpec] = {
    # --------------------------------------------------------------------------
    # Episode 1: Faith Broker - Data Privacy & GDPR Compliance
    # --------------------------------------------------------------------------
    "episode1": EpisodeSpec(
        id="episode1",
        episode_number=1,
        title="Automating Data Privacy & GDPR Compliance",
        subtitle="Zero-Friction PII Governance & Subject Access Requests at Coco Pharmaceuticals",
        lead_persona="Faith Broker",
        persona_username="faithbroker",
        persona_role="HR Director & Data Privacy Officer",
        persona_team="Corporate Governance & Regulatory Compliance",
        business_driver="Regulatory Compliance, Privacy Governance & Risk Mitigation",
        target_audience="Data Privacy Officers, Compliance Directors, Legal Counsel, HR Executives",
        voice_name="en-GB-LibbyNeural",
        voice_locale="en-GB",
        voice_gender="Female",
        voice_accent="British English (Authoritative & Professional)",
        voice_description="Refined, clear British executive tone emphasizing accountability and regulatory rigor.",
        offline_say_voice="Samantha",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Compliance Challenge",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "Hello, I'm Faith Broker, HR Director and Data Privacy Officer at Coco Pharmaceuticals. "
                    "When GDPR, HIPAA, and patient privacy regulations require you to locate, classify, and protect "
                    "every piece of personally identifiable information across hundreds of clinical and employee databases, "
                    "traditional manual audits simply cannot keep up. Today, I'm going to show you how open metadata with "
                    "Egeria turns privacy compliance from a terrifying manual bottleneck into an automated, continuous operational safeguard."
                ),
                slide_title="EPISODE 1: AUTOMATING DATA PRIVACY & GDPR",
                slide_subtitle="Operationalizing Privacy by Design • Faith Broker (Privacy Officer)",
                callouts=[
                    "Challenge: Manual Subject Access Requests (SARs) take weeks of manual investigation",
                    "Risk: GDPR & HIPAA non-compliance penalties and clinical patient exposure",
                    "Egeria Solution: Automated classification tagging and unified metadata lineage",
                    "Security Frameworks: NIST CSF 2.0 & ISO 27001 Statement of Applicability",
                ],
            ),
            SceneSpec(
                number=1,
                title="The Governance Context - Privacy Classifications",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "In our corporate governance council, Chief Data Officer Jules Keeper and I established clear governance classifications. "
                    "Egeria integrates pre-packaged NIST CSF 2.0 and SP 800-53 security controls, aligning directly with our ISO 27001 Statement of Applicability. "
                    "Every asset entering our data estate is automatically evaluated for Confidentiality, Impact, and Retention within fail-closed security zones. "
                    "In my workspace, I can instantly see which clinical trial cohorts contain restricted patient identifiers, and ensure that "
                    "governance action engines enforce masking policies before research data is ever shared."
                ),
                slide_title="GOVERNANCE CLASSIFICATIONS & PRIVACY CONTROLS",
                slide_subtitle="Coco Pharmaceuticals Governance Framework • Policy to Execution",
                callouts=[
                    "Security Content Pack: Built-in NIST CSF 2.0 and NIST SP 800-53 OSCAL catalogs",
                    "Standardized Classifications: Confidentiality, Impact, Criticality, Retention",
                    "Fail-Closed Security Zones: Operational metadata restricted by default",
                    "ISO 27001 Mapping: Statement of Applicability directly linked to data assets",
                ],
            ),
            SceneSpec(
                number=2,
                title="Workspace Navigation - Privacy Role & Team Hierarchy",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "Let's step into the My Profile workspace. Logging in as Faith Broker, the system immediately loads my assigned governance roles. "
                    "Notice my association with the Corporate Privacy Council and HR Leadership team. "
                    "I can drill down into my team hierarchy, verifying that Tanya Tidie in Clinical Records and our data stewards have completed "
                    "their privacy review to-dos for the newest clinical hospital feeds."
                ),
                terminal_cue="Launch uv run my_profile --user faithbroker and inspect Roles & My Team screen",
            ),
            SceneSpec(
                number=3,
                title="Subject Access Request (SAR) & PII Lineage",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "When an employee or clinical trial participant submits a Subject Access Request, we no longer need to email dozens of database administrators. "
                    "Using the unified catalog search and My Network graph, I can trace the entire information supply chain for patient identifiers. "
                    "From raw ingestion tables in PostgreSQL to S3 data lakes and analytics marts, Egeria maps the full lineage and confidential relationships in seconds."
                ),
                terminal_cue="Navigate to Shop for Data and My Network screen, filtering for Restricted PII terms",
            ),
            SceneSpec(
                number=4,
                title="Real-Time Privacy Stewardship & Feedback",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "If a new dataset lacks appropriate retention rules, I can immediately tag a to-do, add an audit comment with Control-N, "
                    "or submit real-time feedback with Control-F directly to the engineering team. "
                    "Our data stewards earn Karma Points for completing privacy validations, making compliance a collaborative, rewarding process."
                ),
                terminal_cue="Open To-Dos table, strike Ctrl+N to add privacy comment, open Ctrl+F feedback modal",
            ),
            SceneSpec(
                number=5,
                title="Business Impact & Executive Takeaways",
                speaker="Faith Broker",
                voice="en-GB-LibbyNeural",
                dialogue=(
                    "By anchoring privacy governance in Egeria's open metadata ecosystem, Coco Pharmaceuticals reduced Subject Access Request response times "
                    "from three weeks down to under two hours, while eliminating the risk of regulatory fines. "
                    "Data privacy is no longer a barrier to research—it's the trusted foundation that enables our scientists to innovate with confidence. "
                    "Thank you for joining me!"
                ),
                slide_title="BUSINESS IMPACT & EXECUTIVE ROI",
                slide_subtitle="Measurable Privacy Outcomes • Coco Pharmaceuticals Case Study",
                callouts=[
                    "95% Reduction in SAR Response Time: From 3 weeks to under 2 hours",
                    "Zero-Defect Audit Readiness: Continuous automated metadata classification",
                    "Fail-Closed Protection: Operational secrets and PII strictly isolated",
                    "Explore Egeria: egeria-project.org • Egeria Security Blog Series Part 7",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 2: Peter Profile - Zero-Touch Data Stewardship
    # --------------------------------------------------------------------------
    "episode2": EpisodeSpec(
        id="episode2",
        episode_number=2,
        title="Zero-Touch Data Stewardship & Curation at Scale",
        subtitle="Automating Cataloging, Glossary Mapping & Stewardship Karma at Coco Pharmaceuticals",
        lead_persona="Peter Profile",
        persona_username="peterprofile",
        persona_role="Information Analyst & Lead Data Steward",
        persona_team="Clinical Trials & Enterprise Data Stewardship",
        business_driver="Data Quality, Semantic Consistency & Curation Productivity",
        target_audience="Data Stewards, Information Analysts, Data Governance Teams, Analytics Engineers",
        voice_name="en-GB-RyanNeural",
        voice_locale="en-GB",
        voice_gender="Male",
        voice_accent="British English (Engaging & Methodical)",
        voice_description="Articulate, energetic British analyst tone showcasing hands-on productivity and stewardship precision.",
        offline_say_voice="Daniel",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Stewardship Dilemma",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "Hi everyone! I'm Peter Profile, Lead Information Analyst and Data Steward at Coco Pharmaceuticals. "
                    "As data stewards, we've all faced the impossible backlog: thousands of database columns arriving every week, "
                    "cryptic abbreviations, missing descriptions, and manual spreadsheets that go out of date the minute you save them. "
                    "Today, I'll demonstrate how Egeria transforms data curation into an automated, streamlined experience right from your terminal."
                ),
                slide_title="EPISODE 2: ZERO-TOUCH DATA STEWARDSHIP",
                slide_subtitle="Curating at Machine Speed • Peter Profile (Information Analyst)",
                callouts=[
                    "Problem: Massive schema volumes and manual glossary mapping backlogs",
                    "Friction: Cryptic physical column names disconnected from business definitions",
                    "Egeria Solution: Automated housekeeping connectors & gamified curation",
                    "Lead Persona: Peter Profile (Information Analyst & Lead Data Steward)",
                ],
            ),
            SceneSpec(
                number=1,
                title="Semantic Glossary Alignment & Housekeeping Connectors",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "At Coco Pharma, we connect technical schemas directly to our enterprise business glossaries using ISA and HASA relationships. "
                    "What makes Egeria 6.3 revolutionary are its automated housekeeping connectors running behind the scenes. "
                    "Pasteur archives completed to-dos while permanently preserving our audit lineage, Mendel deduplicates redundant keyword tags, "
                    "and native reversibility gives us Undo and Restore for any accidental metadata modification."
                ),
                slide_title="SEMANTIC KNOWLEDGE GRAPH & HOUSEKEEPING",
                slide_subtitle="Automated Connectors: Simon, Pasteur & Mendel",
                callouts=[
                    "Automated Housekeeping: Pasteur archives finished tasks, Mendel deduplicates tags",
                    "Standardized Relationships: ISA (specialization) and HASA (composition)",
                    "Native Reversibility: Full Undo and cascading Restore on metadata changes",
                    "Cross-System Consistency: One term definition across Snowflake, Kafka, and PostgreSQL",
                ],
            ),
            SceneSpec(
                number=2,
                title="The Steward Cockpit - Managing Curation To-Dos",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "When I launch the My Profile cockpit, my active curation assignments are already loaded in parallel. "
                    "In the To-Dos panel, I see pending validation requests from clinical researchers like Dr. Tessa Tube and Callie Quartile. "
                    "With Control-T, I can edit my to-do table directly in the terminal, updating progress notes and verifying schema certifications."
                ),
                terminal_cue="Launch uv run my_profile --user peterprofile, navigate to To-Dos, hit Ctrl+T to edit",
            ),
            SceneSpec(
                number=3,
                title="Real-Time Annotation & Discussion Threads",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "Collaboration is built directly into the metadata stream. "
                    "Selecting a newly registered oncology assay dataset, I can press Control-O to view comments left by our lab technicians. "
                    "With Control-N, I add an authoritative steward note confirming the confidence score of 0.98 validated against laboratory assay standards. "
                    "Everyone in the enterprise sees this annotation immediately."
                ),
                terminal_cue="Press Ctrl+O to inspect comments, strike Ctrl+N to add verification comment, Ctrl+K to bookmark",
            ),
            SceneSpec(
                number=4,
                title="Earning Karma Points & Community Leadership",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "Every time I complete a glossary review, resolve a data quality defect, or assist a colleague, Egeria awards Karma Points. "
                    "Our Simon connector calculates these scores periodically in the background, keeping our event bus completely free of noise. "
                    "Governance isn't a chore anymore—it's a transparent, recognized contribution to Coco Pharma's life-saving cancer research."
                ),
                terminal_cue="Navigate to Karma panel and Communities screen, review stewardship contributions",
            ),
            SceneSpec(
                number=5,
                title="Business Impact & Value Realization",
                speaker="Peter Profile",
                voice="en-GB-RyanNeural",
                dialogue=(
                    "With Egeria's automated stewardship toolset, we've increased our cataloged asset coverage to over 98% "
                    "while cutting curation cycle times by seventy percent. "
                    "High-quality, curated metadata is the fuel that powers Coco Pharmaceuticals' AI and research breakthroughs. "
                    "Thanks for watching, and happy cataloging!"
                ),
                slide_title="STEWARDSHIP IMPACT & PRODUCTIVITY GAINS",
                slide_subtitle="Quantifiable Metadata Quality Metrics • Coco Pharmaceuticals",
                callouts=[
                    "98%+ Metadata Coverage: Automated ingestion across all primary data stores",
                    "70% Faster Curation Cycles: Interactive terminal editing and semantic linking",
                    "Zero Maintenance Debt: Pasteur and Mendel eliminate backlog clutter automatically",
                    "Learn More: egeria-project.org • Egeria Release 6.3 Blog Series Part 6",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 3: Dr. Tessa Tube - Clinical Trial Data Provenance
    # --------------------------------------------------------------------------
    "episode3": EpisodeSpec(
        id="episode3",
        episode_number=3,
        title="Trusted Clinical Data Provenance & Trial Integrity",
        subtitle="End-to-End Scientific Audit Trails & Governed Research Subscriptions",
        lead_persona="Dr. Tessa Tube",
        persona_username="tessatube",
        persona_role="Lead Clinical Researcher",
        persona_team="Oncology Research & Clinical Trials",
        business_driver="Scientific Integrity, Regulatory Filings (FDA/EMA) & Audit Provenance",
        target_audience="Clinical Researchers, R&D Directors, Biostatisticians, Regulatory Affairs",
        voice_name="en-US-AriaNeural",
        voice_locale="en-US",
        voice_gender="Female",
        voice_accent="American English (Academic & Authoritative)",
        voice_description="Crisp, mature authoritative academic tone delivering scientific credibility and audit precision.",
        offline_say_voice="Moira",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Scientific Imperative",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "Welcome! I'm Dr. Tessa Tube, Lead Clinical Researcher directing oncology trials at Coco Pharmaceuticals. "
                    "When developing novel cancer therapies, scientific integrity is paramount. "
                    "Regulatory agencies like the FDA and EMA require complete, uncompromised provenance proving that our clinical conclusions "
                    "originate from certified, unmodified laboratory data. "
                    "Let's explore how Egeria provides the unbroken chain of custody our scientific research demands."
                ),
                slide_title="EPISODE 3: CLINICAL DATA PROVENANCE & INTEGRITY",
                slide_subtitle="Unbroken Lineage for Cancer Research • Dr. Tessa Tube (Lead Researcher)",
                callouts=[
                    "Requirement: Bulletproof audit trails for FDA and EMA regulatory filings",
                    "Risk: Data drift, untracked transformations, and unverified assay data",
                    "Egeria Solution: Automated end-to-end provenance graphs and certified data products",
                    "Standards: Bitol Open Data Contract Standard (ODCS) & OpenLineage",
                ],
            ),
            SceneSpec(
                number=1,
                title="The Research Lifecycle & Governance Guarantees",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "In our oncology trials, raw patient data flows from hospital ingress feeds into certified analytical data products. "
                    "Under the governance framework established by Jules Keeper, Egeria extracts five distinct lineage layers: "
                    "from business flows down to column mappings. "
                    "Our Darwin governance engine reconciles runtime OpenLineage pipeline events against declared Bitol data contracts, "
                    "flagging any discrepancy between architectural intent and actual data movement."
                ),
                slide_title="SCIENTIFIC PROVENANCE & DATA GOVERNANCE",
                slide_subtitle="Tracking Data Supply Chains from Clinical Assay to Statistical Model",
                callouts=[
                    "Five Lineage Layers: Business Flow, Data Mesh, System Fabric, Data Fabric, Data Mapping",
                    "Darwin Engine: Reconciles pipeline execution against Bitol ODCS contracts",
                    "Quality Scoring: Laboratory validation metrics and confidence scores (>=0.95)",
                    "High-Speed OpenLineage: Analyzing 800k+ events in seconds via PostgreSQL backend",
                ],
            ),
            SceneSpec(
                number=2,
                title="Shopping for Certified Clinical Data Products",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "In the My Profile workspace, navigating to 'Shop for Data' gives me access to our certified Digital Data Products catalog. "
                    "External hospital trial datasets are imported seamlessly using W3C DCAT version 3 standards. "
                    "I can search for oncology cohort assays, filter by quality score, and inspect the underlying schema. "
                    "With Control-L, I can instantly sample the dataset in a secure sandbox, verifying row counts and distributions "
                    "before ever committing to a full research pipeline."
                ),
                terminal_cue="Navigate to Shop for Data, search for 'Oncology Cohort', press Ctrl+L for data sampling modal",
            ),
            SceneSpec(
                number=3,
                title="Governed Subscription Requests & Usage Terms",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "Once I verify the sample, pressing Control-U opens the Subscription Request modal. "
                    "I specify my clinical trial protocol number, research purpose, and duration under our Bitol ODCS agreement. "
                    "Egeria automatically routes the request through Faith Broker for privacy clearance and Peter Profile for data stewardship, "
                    "while the Baudot connector provisions differential updates without notification spam."
                ),
                terminal_cue="Press Ctrl+U to open Create Subscription Request modal, fill trial protocol, confirm request",
            ),
            SceneSpec(
                number=4,
                title="Cross-Functional Research Collaboration",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "Using the My Network visualization, I can see my collaborative links with data scientist Callie Quartile "
                    "and integration architect Bob Nitter. "
                    "When Callie updates her patient survival prediction model, our research team receives automated notifications, "
                    "ensuring everyone works on the same certified version of clinical truth."
                ),
                terminal_cue="Open My Network screen, examine research relationships and collaborative links",
            ),
            SceneSpec(
                number=5,
                title="Scientific Impact & Accelerated Discovery",
                speaker="Dr. Tessa Tube",
                voice="en-US-AriaNeural",
                dialogue=(
                    "Egeria has revolutionized our clinical trial lifecycle. "
                    "We have eliminated months of audit preparation for regulatory filings and reduced research onboarding times by eighty percent. "
                    "Most importantly, trusted open metadata accelerates our ability to deliver life-saving therapies to patients faster. "
                    "Thank you for exploring clinical provenance with me today!"
                ),
                slide_title="RESEARCH IMPACT & REGULATORY READINESS",
                slide_subtitle="Accelerating Clinical Outcomes • Coco Pharmaceuticals",
                callouts=[
                    "80% Reduction in Audit Preparation: Instant export of complete provenance graphs",
                    "100% Traceability: Every regulatory claim backed by immutable metadata lineage",
                    "Bitol ODCS Compliance: Automated contract enforcement across all trial pipelines",
                    "Explore Egeria: egeria-project.org • Egeria Data Mesh Blog Series Part 8 & 9",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 4: Stew Faster - Supply Chain & ESG Sustainability
    # --------------------------------------------------------------------------
    "episode4": EpisodeSpec(
        id="episode4",
        episode_number=4,
        title="Supply Chain Traceability & ESG Sustainability",
        subtitle="Unifying IoT Telemetry, Carbon Accounting & Factory Operations with Open Metadata",
        lead_persona="Stew Faster",
        persona_username="stewfaster",
        persona_role="Manufacturing General Manager",
        persona_team="Plant Operations & Sustainability Leadership",
        business_driver="ESG Compliance, Operational Efficiency, Carbon Accounting & IoT Telemetry",
        target_audience="COOs, Supply Chain Executives, Sustainability Officers, IoT Engineers",
        voice_name="en-AU-WilliamMultilingualNeural",
        voice_locale="en-AU",
        voice_gender="Male",
        voice_accent="Australian English (Pragmatic & Energetic)",
        voice_description="Direct, pragmatic Australian operational leader tone delivering actionable insights on plant floor efficiency.",
        offline_say_voice="Daniel",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Manufacturing Reality",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "G'day! I'm Stew Faster, Manufacturing General Manager at Coco Pharmaceuticals. "
                    "Running high-precision pharmaceutical plants means juggling thousands of IoT sensors, chemical reactors, "
                    "and cold-chain logistics, while meeting strict corporate ESG and carbon reduction mandates. "
                    "If your operational tech and corporate data lakes don't talk to each other, you're flying blind. "
                    "Today, I'll show you how Egeria connects our factory floor directly into our enterprise metadata catalog."
                ),
                slide_title="EPISODE 4: SUPPLY CHAIN & ESG SUSTAINABILITY",
                slide_subtitle="From Factory Floor to Carbon Ledger • Stew Faster (Manufacturing GM)",
                callouts=[
                    "Challenge: Fragmented operational technology (OT) and corporate IT silos",
                    "ESG Mandate: Real-time carbon tracking, solvent recovery & cold-chain compliance",
                    "Egeria Solution: Unified metadata catalog for IoT telemetry and physical assets",
                    "Open Standards: W3C DCAT v3 JSON-LD Document Exchange",
                ],
            ),
            SceneSpec(
                number=1,
                title="Connecting Physical Assets to Digital Metadata & DCAT v3",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "In our advanced manufacturing plants, every chemical batch reactor, autoclave, and temperature logger "
                    "is cataloged as an Egeria asset under our Technology Types taxonomy. "
                    "With Egeria 6.3's W3C DCAT version 3 connectors—including DCAT Files Receiver and DCAT Publisher—we exchange "
                    "operational datasets with partner suppliers and public registries seamlessly in standard JSON-LD, "
                    "linking physical equipment to real-time carbon and solvent recovery metrics."
                ),
                slide_title="OPERATIONAL TECHNOLOGY & DCAT V3 CATALOGING",
                slide_subtitle="W3C DCAT v3 Connectors: Files, Events, Cataloguers & Publishers",
                callouts=[
                    "W3C DCAT v3 Standards: Interoperable JSON-LD catalog exchange across supply chains",
                    "Technology Types: Standardized catalog for IoT sensors, PLC controllers, and reactors",
                    "Real-Time Telemetry: MQTT and Kafka topic metadata indexed alongside batch records",
                    "ESG Carbon Tracking: Kilowatt-hour and solvent consumption bound to batch IDs",
                ],
            ),
            SceneSpec(
                number=2,
                title="The Plant Manager Dashboard & Roles",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "Launching My Profile, my operational workspace loads our Sustainability & Manufacturing council roles. "
                    "I can see my team links with CFO Reggie Mint and Chief Data Officer Jules Keeper. "
                    "We monitor shared KPIs for energy efficiency and batch yield right from our team activity stream."
                ),
                terminal_cue="Launch uv run my_profile --user stewfaster, inspect Sustainability roles and team panel",
            ),
            SceneSpec(
                number=3,
                title="Exploring Technology Types & Factory Catalogs",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "Navigating to the Technology Types screen, I can inspect the hardware and software connectors powering our plants. "
                    "From SCADA database gateways to Apache NiFi pipelines, Egeria details the operational status and deployment configurations. "
                    "When an autoclave temperature sensor flags an anomaly, we can trace the exact batch and affected ampoules in seconds."
                ),
                terminal_cue="Navigate to Technology Types screen, inspect SCADA and IoT sensor connectors",
            ),
            SceneSpec(
                number=4,
                title="Collaborative Operational Feedback & Actions",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "When our sustainability audit identifies an opportunity for solvent recycling, "
                    "I can open the Feedback dialog with Control-F or log an immediate to-do for our engineering team. "
                    "Using Dr. Egeria markdown reports, our carbon footprint metrics are automatically generated and published to executive leadership."
                ),
                terminal_cue="Strike Ctrl+F for operational feedback, review automated Dr. Egeria sustainability report",
            ),
            SceneSpec(
                number=5,
                title="Operational Outcomes & Sustainability ROI",
                speaker="Stew Faster",
                voice="en-AU-WilliamMultilingualNeural",
                dialogue=(
                    "By bridging the gap between factory floor operations and open metadata governance, "
                    "Coco Pharmaceuticals reduced manufacturing energy waste by eighteen percent and achieved automated, real-time ESG compliance. "
                    "Open metadata isn't just for software developers—it's the backbone of modern, sustainable manufacturing. "
                    "Cheers, and thanks for watching!"
                ),
                slide_title="MANUFACTURING ROI & SUSTAINABILITY IMPACT",
                slide_subtitle="Tangible Operational Gains • Coco Pharmaceuticals",
                callouts=[
                    "18% Reduction in Energy Waste: Real-time sensor telemetry optimization",
                    "Inter-Company Interoperability: Seamless DCAT v3 partner catalog exchange",
                    "Automated ESG Reporting: Dr. Egeria markdown reports generated in minutes",
                    "Learn More: egeria-project.org • Egeria DCAT Exchange Blog Series Part 10",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 5: Erin Overview - Business Glossaries & Architecture
    # --------------------------------------------------------------------------
    "episode5": EpisodeSpec(
        id="episode5",
        episode_number=5,
        title="Connecting Business Glossaries to Technical Architecture",
        subtitle="Eliminating Semantic Ambiguity with Enterprise Knowledge Graphs & Open Metadata",
        lead_persona="Erin Overview",
        persona_username="erinoverview",
        persona_role="Enterprise Information Architect",
        persona_team="Information Architecture & Enterprise Strategy",
        business_driver="Semantic Interoperability, Architecture Governance & Vendor Neutrality",
        target_audience="Enterprise Architects, Chief Architects, Data Modelers, Integration Engineers",
        voice_name="en-US-JennyNeural",
        voice_locale="en-US",
        voice_gender="Female",
        voice_accent="American English (Clear, Strategic & Visionary)",
        voice_description="Articulate, visionary American architectural voice connecting enterprise strategy to technical implementation.",
        offline_say_voice="Samantha",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Tower of Babel",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "Hello! I'm Erin Overview, Enterprise Information Architect at Coco Pharmaceuticals. "
                    "In any large organization, the biggest hurdle to digital transformation is the language barrier. "
                    "Business executives say 'Customer Account', marketing says 'Subscriber Profile', and the database column is named 'CUST_MSTR_01'. "
                    "When terms diverge, data integration fails and AI models produce hallucinations. "
                    "Today, I'll show you how Egeria builds an enterprise knowledge graph that unifies business language and technical architecture."
                ),
                slide_title="EPISODE 5: BUSINESS GLOSSARIES & ARCHITECTURE",
                slide_subtitle="Unified Semantic Architecture • Erin Overview (Information Architect)",
                callouts=[
                    "Problem: Semantic ambiguity and disconnected naming across business and IT",
                    "Cost: Broken ETL pipelines, slow data integration, and untrusted analytics",
                    "Egeria Solution: Open metadata knowledge graph connecting glossaries to schemas",
                    "High-Speed Graph: Five supply-chain lineage layers & PostgreSQL OpenLineage",
                ],
            ),
            SceneSpec(
                number=1,
                title="The Enterprise Taxonomy & Semantic Knowledge Graph",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "At Coco Pharma, we structure our business concepts into Subject Areas, Glossaries, and Controlled Vocabularies. "
                    "Egeria's semantic relationship model allows us to define relationships like 'Is A', 'Has A', and 'Synonym' across terms. "
                    "In Egeria 6.3, our OpenLineage engine processes 30 days of pipeline history—over 800,000 events—in just 3 seconds, "
                    "extracting five clear views from business flows down to physical column transformations with bounded graph queries."
                ),
                slide_title="ENTERPRISE TAXONOMY & RELATIONSHIP ARCHITECTURE",
                slide_subtitle="Federated Open Metadata Across Heterogeneous Technology Platforms",
                callouts=[
                    "Five Lineage Layers: Business Flow, Data Mesh, System Fabric, Data Fabric, Data Mapping",
                    "High Performance: 800k+ OpenLineage events analyzed in ~3 seconds in PostgreSQL",
                    "Bounded Exploration: 8-hop navigation limits prevent browser and terminal freezes",
                    "Vendor Independence: Open standards eliminate proprietary catalog lock-in",
                ],
            ),
            SceneSpec(
                number=2,
                title="Architecture Cockpit & Communities Navigation",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "In my My Profile workspace, I monitor cross-functional architecture initiatives. "
                    "Under the Communities tab, our Architecture Review Board collaborates with API developers like Bob Nitter "
                    "and business leaders like Harry Hopeful. "
                    "We can review newly proposed data product models and verify semantic compliance before code is ever deployed."
                ),
                terminal_cue="Launch uv run my_profile --user erinoverview, open Communities screen and view Architecture Board",
            ),
            SceneSpec(
                number=3,
                title="Browsing the Unified Glossary & Term Dictionaries",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "Let's switch into the Shop for Data and Glossary browser. "
                    "Here, any developer or business analyst can search for business terms like 'Bioequivalence Threshold' "
                    "and immediately see its formal mathematical definition, governance classification, and linked physical datasets. "
                    "With Control-K, I bookmark active architecture standards for rapid recall."
                ),
                terminal_cue="Open Shop for Data, search for 'Bioequivalence', inspect term details, press Ctrl+K to bookmark",
            ),
            SceneSpec(
                number=4,
                title="Graph Visualization of Architectural Dependencies",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "The My Network screen visualizes the interconnected topology of our information supply chain. "
                    "We can see how changes to an upstream hospital schema cascade downstream to clinical research models and executive reports. "
                    "This level of impact analysis makes enterprise architecture proactive rather than reactive."
                ),
                terminal_cue="Open My Network screen, navigate relationship graph and architectural connections",
            ),
            SceneSpec(
                number=5,
                title="Architectural ROI & Strategic Agility",
                speaker="Erin Overview",
                voice="en-US-JennyNeural",
                dialogue=(
                    "By adopting Egeria's open metadata architecture, Coco Pharmaceuticals reduced new data integration project timelines by sixty percent "
                    "and eliminated costly misunderstandings between business teams and engineering. "
                    "A unified semantic foundation is what makes agile, reliable AI possible. "
                    "Thank you for exploring enterprise information architecture with me today!"
                ),
                slide_title="STRATEGIC IMPACT & ARCHITECTURE ROI",
                slide_subtitle="Enabling Enterprise Agility • Coco Pharmaceuticals",
                callouts=[
                    "60% Faster Data Integration: Immediate reuse of pre-mapped semantic models",
                    "Zero Hallucination AI: Grounding LLMs in authoritative open metadata definitions",
                    "Future-Proof Architecture: Open standards ensure complete platform portability",
                    "Explore More: egeria-project.org • Egeria Lineage Layers Blog Series Part 9",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 6: Sidney Seeker - Forensic Auditing & Fraud Investigation
    # --------------------------------------------------------------------------
    "episode6": EpisodeSpec(
        id="episode6",
        episode_number=6,
        title="Forensic Data Auditing & Fraud Investigation",
        subtitle="Uncovering Shadow Pipelines, Unauthorized Changes & Compliance Anomalies with Open Metadata",
        lead_persona="Sidney Seeker",
        persona_username="sidneyseeker",
        persona_role="Lead Fraud Investigator & Security Auditor",
        persona_team="Internal Audit & Security Investigation",
        business_driver="Fraud Detection, Security Compliance, Shadow IT Discovery & Audit Defense",
        target_audience="Internal Auditors, CISOs, Fraud Investigators, Security Analysts, Risk Officers",
        voice_name="en-IE-ConnorNeural",
        voice_locale="en-IE",
        voice_gender="Male",
        voice_accent="Irish English (Sharp, Inquisitive & Methodical)",
        voice_description="Sharp, inquisitive Irish forensic auditor tone highlighting vigilance, evidence integrity, and anomaly detection.",
        offline_say_voice="Daniel",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Hidden Anomaly",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "Hello there! I'm Sidney Seeker, Lead Fraud Investigator and Security Auditor at Coco Pharmaceuticals. "
                    "In modern enterprises, fraud and security breaches rarely announce themselves. "
                    "They hide in unapproved database schema copies, unauthorized pipeline modifications, and subtle changes to financial payment tables. "
                    "When investigating anomalies, you need an immutable, timestamped record of every metadata change. "
                    "Today, I'll show you how Egeria provides the forensic visibility needed to catch discrepancies before they become disasters."
                ),
                slide_title="EPISODE 6: FORENSIC DATA AUDITING & INVESTIGATION",
                slide_subtitle="Time-Travel Lineage & Anomaly Detection • Sidney Seeker (Auditor)",
                callouts=[
                    "Threat: Shadow data pipelines, unapproved replication copies, and invoice tampering",
                    "Audit Challenge: Reconstructing who altered an asset definition and when",
                    "Egeria Solution: STRIDE threat modeling, reversible metadata & audit lineage",
                    "Lead Persona: Sidney Seeker (Lead Fraud Investigator & Auditor)",
                ],
            ),
            SceneSpec(
                number=1,
                title="The Audit Trail - Metadata Versioning & Classifications",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "Under Coco Pharma's zero-trust security architecture, Egeria records every metadata event. "
                    "Egeria 6.3 incorporates standardized STRIDE threat models and fail-closed security zones. "
                    "If an unauthorized change occurs, native reversibility allows us to execute Undo or cascading Restore on affected schemas. "
                    "Working alongside CISO Simon Burr and Payments Clerk Sally Counter, we continuously audit sensitive transactional streams."
                ),
                slide_title="IMMUTABLE AUDITING & THREAT MODELING",
                slide_subtitle="STRIDE Threats, Reversible Metadata & Fail-Closed Zones",
                callouts=[
                    "Built-in STRIDE Threat Models: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation",
                    "Native Reversible Operations: Full Undo and cascading Restore for metadata elements",
                    "Fail-Closed Security Zones: Operational credentials and configs restricted by default",
                    "Cross-System Verification: Matching ERP ledger entries against banking egress feeds",
                ],
            ),
            SceneSpec(
                number=2,
                title="Investigator Workspace & Security Team Drill-Down",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "Launching the My Profile workspace as Sidney Seeker, my active security roles and investigation to-dos are right at my fingertips. "
                    "I can drill down into our Security Investigation Team, checking notes from DevOps specialist Lemmie Stage "
                    "and reviewing open audit alerts across our payment infrastructure."
                ),
                terminal_cue="Launch uv run my_profile --user sidneyseeker, review Audit roles and Security Team drill-down",
            ),
            SceneSpec(
                number=3,
                title="Tracing Payment Anomalies with Lineage & Comments",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "When an anomalous invoice payment is flagged, I navigate to the Accounts Payable data product in Shop for Data. "
                    "Pressing Control-O, I view discussion threads between Sally Counter and our auditors. "
                    "With Control-N, I attach a forensic audit tag to the dataset, flagging it for immediate review and locking down unverified exports."
                ),
                terminal_cue="Open Shop for Data, filter Accounts Payable dataset, hit Ctrl+O for comments, Ctrl+N to log audit tag",
            ),
            SceneSpec(
                number=4,
                title="Uncovering Shadow IT in the Network Graph",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "The My Network graph allows us to spot unapproved data replication instantly. "
                    "If an uncataloged server is pulling sensitive patient or payment records from our core databases, "
                    "Egeria's relationship visualizer highlights the unauthorized relationship, allowing us to isolate the system immediately."
                ),
                terminal_cue="Open My Network screen, examine anomalous relationship clusters and unauthorized links",
            ),
            SceneSpec(
                number=5,
                title="Investigation Outcomes & Risk Protection",
                speaker="Sidney Seeker",
                voice="en-IE-ConnorNeural",
                dialogue=(
                    "With Egeria's comprehensive metadata forensics, Coco Pharmaceuticals has eliminated shadow data copies "
                    "and reduced internal investigation cycle times by eighty-five percent. "
                    "Proactive metadata governance is the ultimate shield protecting enterprise reputation and financial integrity. "
                    "Stay vigilant, and thank you for watching!"
                ),
                slide_title="AUDIT IMPACT & SECURITY ROI",
                slide_subtitle="Protecting Enterprise Integrity • Coco Pharmaceuticals",
                callouts=[
                    "85% Faster Investigation Cycles: Instant reconstruction of data history and access logs",
                    "Zero Unmonitored Shadow IT: Continuous discovery of rogue data copies",
                    "Reversible Recovery: Instant Restore on deleted or compromised catalog assets",
                    "Explore Egeria: egeria-project.org • Egeria Security Blog Series Part 7",
                ],
            ),
        ],
    ),

    # --------------------------------------------------------------------------
    # Episode 7: Jules Keeper & Reggie Mint - The Executive Cockpit
    # --------------------------------------------------------------------------
    "episode7": EpisodeSpec(
        id="episode7",
        episode_number=7,
        title="The Executive Cockpit: Measuring Data ROI & Strategy",
        subtitle="Transforming Data Governance from a Cost Center into a Value Creation Engine",
        lead_persona="Jules Keeper & Reggie Mint",
        persona_username="juleskeeper",
        persona_role="Chief Data Officer & Chief Financial Officer",
        persona_team="Executive Board & Strategic Leadership",
        business_driver="Data Valuation, Executive ROI, Strategic Governance & Board Reporting",
        target_audience="CDOs, CFOs, CIOs, CEOs, Board Directors, Enterprise Leaders",
        voice_name="en-GB-ThomasNeural",
        voice_locale="en-GB",
        voice_gender="Male",
        voice_accent="British English (Executive, Warm & Authoritative)",
        voice_description="Distinguished British executive tone paired with American CFO dialogue illustrating strategic leadership.",
        offline_say_voice="Daniel",
        scenes=[
            SceneSpec(
                number=0,
                title="Cold Open - The Boardroom Challenge",
                speaker="Jules Keeper",
                voice="en-GB-ThomasNeural",
                dialogue=(
                    "Welcome back to Coco Pharmaceuticals. I'm Jules Keeper, Chief Data Officer, joined by our Chief Financial Officer, Reggie Mint. "
                    "Every executive team asks the fundamental question: Is our investment in data governance actually moving the needle? "
                    "Historically, data governance was viewed as a bureaucratic cost center that slowed business velocity. "
                    "Today, Reggie and I will show you how Egeria transforms open metadata into a measurable engine of enterprise value, innovation, and return on investment."
                ),
                slide_title="EPISODE 7: THE EXECUTIVE COCKPIT",
                slide_subtitle="Measuring Data ROI & Strategic Value • Jules Keeper (CDO) & Reggie Mint (CFO)",
                callouts=[
                    "Executive Challenge: Quantifying the business ROI of data governance initiatives",
                    "Legacy Trap: Bureaucratic policy documents disconnected from daily operations",
                    "Egeria Solution: Actionable metadata cockpits, product subscriptions & measurable KPI tracking",
                    "Standards & Automation: Bitol ODCS contracts, autonomous housekeeping & fail-closed security",
                ],
            ),
            SceneSpec(
                number=1,
                title="Executive Alignment - Governance Linked to Business Imperatives",
                speaker="Jules Keeper",
                voice="en-GB-ThomasNeural",
                dialogue=(
                    "When we launched our 'Better Data for Everyone' initiative, we anchored every governance policy to concrete business imperatives: "
                    "accelerating clinical cancer trials with Dr. Tessa Tube, ensuring zero-breach privacy with Faith Broker, "
                    "and optimizing manufacturing energy efficiency with Stew Faster. "
                    "Attaching governance responsibilities to appointed operational roles turned abstract policy into measurable daily accountability."
                ),
                slide_title="STRATEGIC GOVERNANCE IMPERATIVES",
                slide_subtitle="Aligning Open Metadata Directly with Strategic Business Goals",
                callouts=[
                    "Clinical Innovation: Accelerating trial filings from years to months",
                    "Regulatory Protection: Zero-defect compliance across GDPR, HIPAA, and financial audits",
                    "Operational Sustainability: 18% energy waste reduction across manufacturing plants",
                    "Role-Based Execution: Policies bound to appointed team members across the enterprise",
                ],
            ),
            SceneSpec(
                number=2,
                title="Executive Cockpit Walkthrough & Portfolio Health",
                speaker="Jules Keeper",
                voice="en-GB-ThomasNeural",
                dialogue=(
                    "Logging into the executive cockpit, Reggie and I have real-time visibility across Coco Pharma's entire data estate. "
                    "In our executive associations, we oversee active Digital Data Product subscriptions adhering to Bitol standards, "
                    "monitor autonomous housekeeping efficiency, and review strategic cross-functional initiatives across all business units."
                ),
                terminal_cue="Launch uv run my_profile --user juleskeeper, inspect Executive associations and data product portfolios",
            ),
            SceneSpec(
                number=3,
                title="CFO Perspective - Quantifying Data ROI & Risk Reduction",
                speaker="Reggie Mint",
                voice="en-US-GuyNeural",
                dialogue=(
                    "From a financial standpoint, Egeria delivers measurable bottom-line value. "
                    "We've reduced data discovery overhead by seventy-five percent across our three hundred analysts, saving thousands of productive hours each month. "
                    "By eliminating shadow data infrastructure and retiring duplicate legacy tools, we cut enterprise licensing costs by over two million dollars annually."
                ),
                terminal_cue="Navigate to Shop for Data and Active Subscriptions, demonstrating enterprise usage metrics",
            ),
            SceneSpec(
                number=4,
                title="Community Engagement & Collaborative Governance",
                speaker="Jules Keeper",
                voice="en-GB-ThomasNeural",
                dialogue=(
                    "Governance succeeds when it's embraced by people, not mandated from an ivory tower. "
                    "Our Karma Points leaderboard and Community forums empower practitioners like Callie Quartile and Peter Profile "
                    "to take pride in data excellence. Culture and technology working in unison is what makes Coco Pharmaceuticals an industry leader."
                ),
                terminal_cue="Open Communities and Karma panel, reviewing enterprise participation leaderboard",
            ),
            SceneSpec(
                number=5,
                title="The Future of Governed Enterprise Intelligence",
                speaker="Jules Keeper",
                voice="en-GB-ThomasNeural",
                dialogue=(
                    "Open metadata is the essential foundation for reliable AI, regulatory trust, and sustainable business growth. "
                    "We invite you to explore Egeria's open source ecosystem, try out the Coco Pharmaceuticals personas, "
                    "and bring the power of open metadata to your own organization. "
                    "Thank you for watching the Coco Pharmaceuticals Business Value Series!"
                ),
                slide_title="THE EXECUTIVE SUMMARY & CALL TO ACTION",
                slide_subtitle="Delivering 'Better Data for Everyone' • Coco Pharmaceuticals",
                callouts=[
                    "$2M+ Annual Infrastructure Savings: Consolidated catalog and reduced tool redundancy",
                    "75% Faster Analyst Discovery: Immediate access to governed digital data products",
                    "Autonomous Housekeeping: Simon, Pasteur, and Baudot maintain clean metadata 24/7",
                    "Join the Movement: egeria-project.org • github.com/odpi/egeria",
                ],
            ),
        ],
    ),
}
