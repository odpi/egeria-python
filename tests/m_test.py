from pyegeria.mermaid_utilities import construct_mermaid_web, construct_mermaid_jup, render_mermaid

m = """
---
title: Component for Solution Blueprint - Clinical Trial Management Solution Blueprint [c4f8d707-7c85-4125-b5fd-c3257a2ef2ef]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

subgraph c4f8d707-7c85-4125-b5fd-c3257a2ef2ef [Components and Actors]
fc2de77f-7320-48ea-8750-d434c6e870db@{ shape: text, label: "*Description*
**A description of how a clinical trial is managed in Coco Pharmaceuticals.**"}
37b8560d-84d4-434b-9b0d-105420fcc924@{ shape: subproc, label: "*Solution Component*
**Certify Hospital**"}
f37f3735-28a1-4e03-9ff5-3fe2f137f661@{ shape: trap-t, label: "*Solution Actor Role*
**Clinical Trial Manager**"}
f37f3735-28a1-4e03-9ff5-3fe2f137f661-->|"Certifier"|37b8560d-84d4-434b-9b0d-105420fcc924
72a86eec-9734-4bc0-babb-4fec0aa7c9ff@{ shape: docs, label: "*Solution Component*
**Assemble Treatment Assessment Report**"}
48bc201e-3d4e-4beb-bdb2-0fd9d134f6d5@{ shape: rect, label: "*Solution Component*
**Treatment Efficacy Evidence**"}
48bc201e-3d4e-4beb-bdb2-0fd9d134f6d5-->|"Solution Linking Wire"|72a86eec-9734-4bc0-babb-4fec0aa7c9ff
f37f3735-28a1-4e03-9ff5-3fe2f137f661-->|"Author"|72a86eec-9734-4bc0-babb-4fec0aa7c9ff
b5c8da4c-f925-4cf1-8294-e43cd2c1a584@{ shape: rect, label: "*Solution Component*
**Analyse Patient Data**"}
b5c8da4c-f925-4cf1-8294-e43cd2c1a584-->|"Solution Linking Wire"|48bc201e-3d4e-4beb-bdb2-0fd9d134f6d5
7f5dca65-50b4-4103-9ac7-3a406a09047a@{ shape: subproc, label: "*Solution Component*
**Weekly Measurements Onboarding Pipeline**"}
07705e15-efff-4f80-8992-f04ac85e0ef1@{ shape: rect, label: "*Solution Component*
**Landing Folder Cataloguer**"}
07705e15-efff-4f80-8992-f04ac85e0ef1-->|"Solution Linking Wire"|7f5dca65-50b4-4103-9ac7-3a406a09047a
f37f3735-28a1-4e03-9ff5-3fe2f137f661-->|"Steward"|7f5dca65-50b4-4103-9ac7-3a406a09047a
b0290339-c96c-4b05-904f-12fc98e54e14@{ shape: trap-t, label: "*Solution Actor Role*
**Certified Data Engineer**"}
b0290339-c96c-4b05-904f-12fc98e54e14-->|"Steward"|7f5dca65-50b4-4103-9ac7-3a406a09047a
d48f579f-76d3-4c49-b1b4-575f5645a9d0@{ shape: lin-cyl, label: "*Solution Component*
**Treatment Validation Sandbox**"}
26c07ca4-3b8e-484b-812b-36c1ace4b275@{ shape: rect, label: "*Solution Component*
**Populate Sandbox**"}
26c07ca4-3b8e-484b-812b-36c1ace4b275-->|"Solution Linking Wire"|d48f579f-76d3-4c49-b1b4-575f5645a9d0
ee2bb773-e630-4cf9-bdf1-7c2dd64fe4ec@{ shape: processes, label: "*Solution Component*
**Hospital Processes**"}
a8bd84ca-0aae-4534-b0e8-87e8659467a6@{ shape: trap-t, label: "*Solution Actor Role*
**Clinical Trial Participating Hospital Coordinator**"}
a8bd84ca-0aae-4534-b0e8-87e8659467a6-->|"Coordinator on behalf of hospital"|ee2bb773-e630-4cf9-bdf1-7c2dd64fe4ec
30adaab5-8870-47a8-8ae9-facbf84cb05a@{ shape: trap-t, label: "*Solution Actor Role*
**Clinical Trial Participating Hospital**"}
30adaab5-8870-47a8-8ae9-facbf84cb05a-->|"Owner"|ee2bb773-e630-4cf9-bdf1-7c2dd64fe4ec
d48f579f-76d3-4c49-b1b4-575f5645a9d0-->|"Solution Linking Wire"|b5c8da4c-f925-4cf1-8294-e43cd2c1a584
ece17806-836c-4756-b3a2-2d12dde215f6@{ shape: trap-t, label: "*Solution Actor Role*
**New Treatment Data Scientist**"}
ece17806-836c-4756-b3a2-2d12dde215f6-->|"Data Analyser"|b5c8da4c-f925-4cf1-8294-e43cd2c1a584
0c757e35-8a42-4d5f-b01b-c72a6cea65cc@{ shape: trap-t, label: "*Solution Actor Role*
**New Treatment Researcher.**"}
0c757e35-8a42-4d5f-b01b-c72a6cea65cc-->|"Results Interpreter"|b5c8da4c-f925-4cf1-8294-e43cd2c1a584
e9c2f911-ffcb-40c6-aeee-8c4d43811576@{ shape: subproc, label: "*Solution Component*
**Onboard Hospital**"}
b0290339-c96c-4b05-904f-12fc98e54e14-->|"Initiator"|e9c2f911-ffcb-40c6-aeee-8c4d43811576
849b0b42-f465-452b-813c-477d6398e082@{ shape: subproc, label: "*Solution Component*
**Set up clinical trial**"}
f37f3735-28a1-4e03-9ff5-3fe2f137f661-->|"Initiator"|849b0b42-f465-452b-813c-477d6398e082
a5d4d638-6836-47e5-99d0-fdcde637e13f@{ shape: lin-cyl, label: "*Solution Component*
**Weekly Measurements Data Lake Folder**"}
7f5dca65-50b4-4103-9ac7-3a406a09047a-->|"Solution Linking Wire"|a5d4d638-6836-47e5-99d0-fdcde637e13f
0bf2547c-937c-41b6-814f-6284849271a1@{ shape: odd, label: "*Solution Component*
**Treatment Assessment Report Validation and Delivery**"}
72a86eec-9734-4bc0-babb-4fec0aa7c9ff-->|"Solution Linking Wire"|0bf2547c-937c-41b6-814f-6284849271a1
f6bc847b-868d-43cc-b767-41f5fe3e47d1@{ shape: trap-t, label: "*Solution Actor Role*
**Clinical Trial Sponsor**"}
f6bc847b-868d-43cc-b767-41f5fe3e47d1-->|"Reviewer"|0bf2547c-937c-41b6-814f-6284849271a1
a5d4d638-6836-47e5-99d0-fdcde637e13f-->|"Solution Linking Wire"|26c07ca4-3b8e-484b-812b-36c1ace4b275
fb32bef2-e79f-4893-b500-2e547f24d482@{ shape: subproc, label: "*Solution Component*
**Set up Data Lake Folder**"}
b0290339-c96c-4b05-904f-12fc98e54e14-->|"Initiator"|fb32bef2-e79f-4893-b500-2e547f24d482
1c150d6e-30cf-481c-9afb-3b06c9c9e78f@{ shape: lin-cyl, label: "*Solution Component*
**Hospital Landing Area Folder**"}
ee2bb773-e630-4cf9-bdf1-7c2dd64fe4ec-->|"Solution Linking Wire"|1c150d6e-30cf-481c-9afb-3b06c9c9e78f
1c150d6e-30cf-481c-9afb-3b06c9c9e78f-->|"Solution Linking Wire"|07705e15-efff-4f80-8992-f04ac85e0ef1
11c7c850-c67c-41cc-9423-d74db47cbf3a@{ shape: subproc, label: "*Solution Component*
**Nominate Hospital**"}
f37f3735-28a1-4e03-9ff5-3fe2f137f661-->|"Initiator"|11c7c850-c67c-41cc-9423-d74db47cbf3a
end
style 48bc201e-3d4e-4beb-bdb2-0fd9d134f6d5 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style ece17806-836c-4756-b3a2-2d12dde215f6 color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style e9c2f911-ffcb-40c6-aeee-8c4d43811576 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style a5d4d638-6836-47e5-99d0-fdcde637e13f color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 0bf2547c-937c-41b6-814f-6284849271a1 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 30adaab5-8870-47a8-8ae9-facbf84cb05a color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style b0290339-c96c-4b05-904f-12fc98e54e14 color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style 26c07ca4-3b8e-484b-812b-36c1ace4b275 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 1c150d6e-30cf-481c-9afb-3b06c9c9e78f color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 07705e15-efff-4f80-8992-f04ac85e0ef1 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style a8bd84ca-0aae-4534-b0e8-87e8659467a6 color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style 0c757e35-8a42-4d5f-b01b-c72a6cea65cc color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style c4f8d707-7c85-4125-b5fd-c3257a2ef2ef color:#3079ab, fill:#b7c0c7, stroke:#3079ab
style 37b8560d-84d4-434b-9b0d-105420fcc924 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 11c7c850-c67c-41cc-9423-d74db47cbf3a color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style fc2de77f-7320-48ea-8750-d434c6e870db color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 849b0b42-f465-452b-813c-477d6398e082 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 7f5dca65-50b4-4103-9ac7-3a406a09047a color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style ee2bb773-e630-4cf9-bdf1-7c2dd64fe4ec color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style 72a86eec-9734-4bc0-babb-4fec0aa7c9ff color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style b5c8da4c-f925-4cf1-8294-e43cd2c1a584 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style f6bc847b-868d-43cc-b767-41f5fe3e47d1 color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style d48f579f-76d3-4c49-b1b4-575f5645a9d0 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
style f37f3735-28a1-4e03-9ff5-3fe2f137f661 color:#FFFFFF, fill:#AA00FF, stroke:#E1D5E7
style fb32bef2-e79f-4893-b500-2e547f24d482 color:#FFFFFF, fill:#838cc7, stroke:#3079ab
"""

h = construct_mermaid_web(m)
print(h)
with open("test_w.html", "w") as f:
    f.write(h)

h = render_mermaid(m)
print(h)
with open("test_j.html", "w") as f:
    f.write(h)