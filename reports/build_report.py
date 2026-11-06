from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"C:\Users\DELL\OneDrive\Desktop\Final_year_PJ-main")
OUT = ROOT / "reports"
OUT.mkdir(exist_ok=True)
DOCX = OUT / "DEPA_Academic_Credential_Exchange_Project_Report.docx"
NAVY, BLUE, PALE, LIGHT, WHITE = "17365D", "1F4E79", "D9EAF7", "F2F6FA", "FFFFFF"


def shade(cell, color):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(shd)


def table(doc, headers, rows, size=8.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    header = t.rows[0]
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    header._tr.get_or_add_trPr().append(repeat)
    for cell, text in zip(header.cells, headers):
        cell.text = str(text)
        shade(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for r in cell.paragraphs[0].runs:
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(size)
            r.font.color.rgb = RGBColor.from_string(WHITE)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for cell, text in zip(cells, row):
            cell.text = str(text)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2:
                shade(cell, LIGHT)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(size)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


def para(doc, text="", align=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.08
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.italic = italic
    return p


def heading(doc, text, level=1):
    p = doc.add_heading(text, level)
    p.paragraph_format.keep_with_next = True
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.add_run(text)


def number(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)


def page(doc):
    doc.add_page_break()


def field(run, code):
    for tag, value in (("begin", None), ("instrText", code), ("separate", None)):
        e = OxmlElement("w:fldChar" if tag != "instrText" else "w:instrText")
        if tag == "begin":
            e.set(qn("w:fldCharType"), value or tag)
        elif tag == "separate":
            e.set(qn("w:fldCharType"), tag)
        else:
            e.set(qn("xml:space"), "preserve")
            e.text = value
        run._r.append(e)
    t = OxmlElement("w:t")
    t.text = "1"
    run._r.append(t)
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    run._r.append(e)


doc = Document()
sec = doc.sections[0]
sec.top_margin, sec.bottom_margin = Inches(.72), Inches(.68)
sec.left_margin = sec.right_margin = Inches(.82)
sec.header_distance = sec.footer_distance = Inches(.32)
normal = doc.styles["Normal"]
normal.font.name, normal.font.size = "Times New Roman", Pt(10.5)
for name, size, color in (
    ("Title", 25, NAVY), ("Heading 1", 16, NAVY),
    ("Heading 2", 12, BLUE), ("Heading 3", 10.5, BLUE),
):
    st = doc.styles[name]
    st.font.name, st.font.size, st.font.bold = "Times New Roman", Pt(size), True
    st.font.color.rgb = RGBColor.from_string(color)
    st.paragraph_format.space_before = Pt(11)
    st.paragraph_format.space_after = Pt(6)
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = hp.add_run("DEPA ACADEMIC CREDENTIAL EXCHANGE  |  PROJECT REPORT")
r.font.name, r.font.size = "Times New Roman", Pt(8)
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run("ANITS  |  2026-2027  |  Page ")
r.font.name, r.font.size = "Times New Roman", Pt(8)
field(fp.add_run(), "PAGE")

# Cover page
for _ in range(2):
    para(doc)
p = para(doc, "ANIL NEERUKONDA INSTITUTE OF TECHNOLOGY AND SCIENCES",
         WD_ALIGN_PARAGRAPH.CENTER)
p.runs[0].bold, p.runs[0].font.size = True, Pt(15)
p.runs[0].font.color.rgb = RGBColor.from_string(NAVY)
para(doc, "(Autonomous)  |  Department of Computer Science and Engineering",
     WD_ALIGN_PARAGRAPH.CENTER)
for _ in range(2):
    para(doc)
p = para(doc, "PROJECT REPORT", WD_ALIGN_PARAGRAPH.CENTER)
p.runs[0].bold, p.runs[0].font.size = True, Pt(15)
p = para(doc, "Consent-Centric Academic Credential Exchange Network",
         WD_ALIGN_PARAGRAPH.CENTER)
p.runs[0].bold, p.runs[0].font.size = True, Pt(23)
p.runs[0].font.color.rgb = RGBColor.from_string(NAVY)
para(doc, "A DEPA-inspired system for student-controlled, field-scoped academic data sharing",
     WD_ALIGN_PARAGRAPH.CENTER, italic=True)
for _ in range(2):
    para(doc)
para(doc, "Submitted in partial fulfillment of the requirements for the degree of",
     WD_ALIGN_PARAGRAPH.CENTER)
p = para(doc, "BACHELOR OF TECHNOLOGY", WD_ALIGN_PARAGRAPH.CENTER)
p.runs[0].bold = True
para(doc, "in Computer Science and Engineering", WD_ALIGN_PARAGRAPH.CENTER)
para(doc, "Academic Year 2026-2027", WD_ALIGN_PARAGRAPH.CENTER)
table(doc, ["PROJECT TEAM", "ROLL NUMBER"], [
    ("M. Ashok", "A23126510102"), ("K. Varun", "A23126510037"),
    ("R. Rupesh", "A23126510112"), ("T. Siddardha", "A23126510120"),
    ("M. Shoheb", "A23126510226"),
])
para(doc, "Project Guide: Dr. Dasari Naga Tej, Associate Professor, Department of CSE",
     WD_ALIGN_PARAGRAPH.CENTER)
para(doc, "Visakhapatnam, Andhra Pradesh  |  06 November 2026",
     WD_ALIGN_PARAGRAPH.CENTER)
page(doc)

heading(doc, "BONAFIDE CERTIFICATE")
para(doc, "This is to certify that the project report entitled “Consent-Centric Academic Credential Exchange Network” is a bonafide record of the project work carried out by the students listed below, under the guidance of Dr. Dasari Naga Tej, Associate Professor, Department of Computer Science and Engineering, Anil Neerukonda Institute of Technology and Sciences, during the academic year 2026-2027.")
table(doc, ["Student", "Roll Number"], [
    ("M. Ashok", "A23126510102"), ("K. Varun", "A23126510037"),
    ("R. Rupesh", "A23126510112"), ("T. Siddardha", "A23126510120"),
    ("M. Shoheb", "A23126510226"),
])
para(doc, "The work is submitted in partial fulfillment of the requirements for the Bachelor of Technology degree in Computer Science and Engineering.")
table(doc, ["Project Guide", "Head of Department", "Dean – Training"], [
    ("Dr. Dasari Naga Tej\nAssociate Professor, CSE",
     "Prof. Srinivas Gorla\nDepartment of CSE",
     "Prof. P. Padmaja\nANITS"),
], 8)
para(doc, "Date: ____________________     Place: Visakhapatnam",
     WD_ALIGN_PARAGRAPH.CENTER)
page(doc)

heading(doc, "ACKNOWLEDGEMENT")
para(doc, "We express our sincere gratitude to our project guide, Dr. Dasari Naga Tej, Associate Professor, Department of Computer Science and Engineering, for his guidance, review, and encouragement throughout this project.")
para(doc, "We thank the Head of the Department, Prof. Srinivas Gorla, and the Dean – Training, Prof. P. Padmaja, for institutional support. We also acknowledge the faculty and staff of ANITS, our teammates, and our families for their suggestions and assistance.")
page(doc)

heading(doc, "DECLARATION")
para(doc, "We hereby declare that the project work presented in this report, entitled “Consent-Centric Academic Credential Exchange Network,” was carried out by us under the guidance of Dr. Dasari Naga Tej. This report is an original account of the project implementation and verification performed by the team. Sources and standards consulted are cited in the References section.")
para(doc, "Illustrative interface values shown in repository screenshots are identified as such and are not represented as measured operational results.")
table(doc, ["Name", "Roll Number", "Signature"], [
    ("M. Ashok", "A23126510102", ""), ("K. Varun", "A23126510037", ""),
    ("R. Rupesh", "A23126510112", ""), ("T. Siddardha", "A23126510120", ""),
    ("M. Shoheb", "A23126510226", ""),
])
para(doc, "Place: Visakhapatnam     Date: ____________________")
page(doc)

heading(doc, "ABSTRACT")
para(doc, "Academic records are often shared through manual document exchange or institution-specific systems. These approaches can make verification slow and disclose more student information than a recipient needs. This project implements a DEPA-inspired, consent-centric academic credential exchange across three services: a Consent Manager, College A as the academic data provider, and College B as the data consumer.")
para(doc, "The Consent Manager manages institutional identities, consent requests, field-level approvals, access grants, request lifecycle, and audit records. College A maintains student academic data and exposes scoped provider access. College B initiates requests and provides student-facing approval, rejection, history, and revocation workflows. The provider validates signed access claims and checks grant status before extracting only approved canonical fields. The institution-to-institution exchange includes an ECDH key agreement and AES-GCM utility; service assertions and access claims use signed JWTs.")
para(doc, "Recorded backend verification totals 96 passing tests (26 Consent Manager, 42 College A, 28 College B), with zero failures, errors, or skipped tests in the available Surefire reports. At report preparation, all three backend health endpoints returned HTTP 200. These checks do not establish production readiness, throughput, or exhaustive end-to-end coverage. The project demonstrates a modular prototype for explicit consent, minimal disclosure, and verifiable academic data exchange.")
para(doc, "Keywords: DEPA, consent management, academic credentials, data minimization, JWT, ECDH, AES-GCM, Spring Boot.")
page(doc)

heading(doc, "TABLE OF CONTENTS")
para(doc, "Contents")
for item in [
    "1. Introduction and Problem Statement ........................................ 7",
    "2. Software Requirements Specification ......................................... 8",
    "3. Related Concepts and Design Rationale ..................................... 10",
    "4. System Architecture and Workflow ............................................. 11",
    "5. Database Design and Data Model ............................................... 12",
    "6. Implementation, Testing, and Results ........................................ 13",
    "7. User Manual and Operations ..................................................... 17",
    "8. Conclusion, Limitations, and Future Work ................................. 18",
    "References ................................................................................... 19",
    "Appendix A: Module Directory ....................................................... 20",
    "Appendix B: Selected API Groups .................................................. 20",
    "Appendix C: Verification Snapshot ................................................ 20",
]:
    para(doc, item)
heading(doc, "LIST OF FIGURES", 2)
para(doc, "Figure 1. Consent Manager interface (illustrative repository capture)\nFigure 2. College A provider interface (illustrative repository capture)\nFigure 3. College B consumer interface (illustrative repository capture)")
heading(doc, "LIST OF TABLES", 2)
para(doc, "Tables cover team members, requirements, service responsibilities, data entities, test results, deployment ports, and operating procedures.")

# Chapter 1
page(doc)
heading(doc, "1. INTRODUCTION AND PROBLEM STATEMENT")
heading(doc, "1.1 Background", 2)
para(doc, "Institutions need to validate enrollment, transcripts, degrees, and other academic attributes. The source institution remains authoritative while a recipient needs reliable evidence for a defined purpose. A student-centered exchange should make the source, recipient, purpose, scope, and lifecycle of each disclosure explicit.")
heading(doc, "1.2 Problem Statement", 2)
para(doc, "The project addresses the need for a controlled mechanism that lets a student authorize an academic-data request without transferring an unrestricted dossier. The system identifies participating institutions, records requests and decisions, enforces approved-field scope at the provider, supports revocation, and provides an auditable workflow across separate services.")
heading(doc, "1.3 Objectives", 2)
for x in [
    "Model three cooperating nodes: Consent Manager, provider (College A), and consumer (College B).",
    "Support authentication and role-specific administrative and student workflows.",
    "Allow consent requests with purpose and requested fields; let students approve selected fields, reject, inspect history, or revoke access.",
    "Issue and validate scoped grants and signed claims; check grant status before provider disclosure.",
    "Map source fields to a canonical response and return only currently authorized fields.",
    "Provide operational pages, bulk student registration, health checks, and automated backend tests.",
]:
    bullet(doc, x)
heading(doc, "1.4 Scope and Boundaries", 2)
para(doc, "The delivered scope is a locally deployable academic-data sharing prototype. It is not a production accreditation platform, national identity system, or formally certified DEPA deployment. Production use requires institution-approved identity proofing, key custody, privacy/legal review, hardening, monitoring, backup, and controlled operations.")
heading(doc, "1.5 Stakeholders", 2)
table(doc, ["Stakeholder", "Responsibility"], [
    ("Student / data principal", "Review recipient, purpose, fields, and consent lifecycle."),
    ("College A / provider", "Maintain authoritative data and disclose within active grant scope."),
    ("College B / consumer", "Request data for a stated purpose and handle retrieved values responsibly."),
    ("Consent Manager", "Coordinate institutional trust, consent, grant status, and audit records."),
    ("Institution administrator", "Manage local users, students, onboarding, and operational tasks."),
])

# Chapter 2
page(doc)
heading(doc, "2. SOFTWARE REQUIREMENTS SPECIFICATION")
heading(doc, "2.1 System Overview", 2)
para(doc, "The system has three backend services and three browser frontends. The Consent Manager is authoritative for consent and grant lifecycle. College A stores provider-side records. College B initiates requests and hosts consumer/student workflows. Service communication is HTTP-based in local development; deployments should use TLS and institution-managed secrets.")
heading(doc, "2.2 Actors and Use Cases", 2)
table(doc, ["Actor", "Use cases"], [
    ("Student", "Authenticate; view inbox/history; approve selected fields, reject, or revoke consent."),
    ("Provider registrar", "Enroll/bulk-register students; view records; manage provider operations."),
    ("Consumer administrator", "Onboard provider metadata; submit requests; monitor retrieval."),
    ("Consent administrator", "Manage organizations, users, consent artifacts, grants, audit views."),
    ("System services", "Validate assertions/grants; map approved fields; record workflow events."),
])
heading(doc, "2.3 Functional Requirements", 2)
table(doc, ["ID", "Requirement"], [
    ("FR-01", "Separate consent governance, academic data provision, and data consumption services."),
    ("FR-02", "Maintain organizations/users and role-protect administrative operations."),
    ("FR-03", "Create requests with data principal, source, purpose, and requested field scope."),
    ("FR-04", "Allow students to review requests, approve selected fields, reject, and inspect history."),
    ("FR-05", "Allow revocation; subsequent provider access must be denied after grant validation."),
    ("FR-06", "Issue scoped access grants and signed claims for approved requests."),
    ("FR-07", "Validate token signature/claims and verify active grant before provider disclosure."),
    ("FR-08", "Return only supported canonical fields approved by the Consent Manager."),
    ("FR-09", "Display mapped provider responses and preserve user navigation state."),
    ("FR-10", "Support student management and bulk registration with college-specific CSV headers."),
    ("FR-11", "Expose unauthenticated health endpoints for process availability checks."),
    ("FR-12", "Record audit/request lifecycle data and provide operational views."),
])
heading(doc, "2.4 Non-Functional Requirements", 2)
table(doc, ["Attribute", "Requirement / status"], [
    ("Security", "Role-protected routes, signed assertions/access claims, fail-closed scope and grant checks."),
    ("Privacy", "Minimize disclosure to explicitly approved canonical fields."),
    ("Integrity", "Cryptographic signatures and authenticated-encryption utility."),
    ("Availability", "Health endpoints exist; production availability target is not measured."),
    ("Interoperability", "HTTP/JSON APIs and canonical field aliases between schemas."),
    ("Maintainability", "Separate modules, persistence entities, controllers, UI routes, and tests."),
    ("Usability", "Role-oriented pages, status labels, searchable records, explicit consent actions."),
])
heading(doc, "2.5 Constraints and Assumptions", 2)
for x in [
    "A student identifier links the request to a provider record; reliable identity proofing is outside scope.",
    "Development ports/configuration are for a trusted local environment, not internet-facing deployment.",
    "CSV imports require documented headers; quoting and embedded commas need validation for arbitrary files.",
    "Correct disclosure depends on consistent field identifiers and aligned signing-key registration.",
]:
    bullet(doc, x)

# Chapter 3
page(doc)
heading(doc, "3. RELATED CONCEPTS AND DESIGN RATIONALE")
heading(doc, "3.1 DEPA-Inspired Data Empowerment", 2)
para(doc, "The design follows the principle that individuals should authorize and control a purpose-specific flow of personal information. Consent is an explicit request and lifecycle-managed grant rather than unrestricted permission. This is an academic prototype informed by the principle, not an official DEPA certification.")
heading(doc, "3.2 Scoped Authorization and Signed Claims", 2)
para(doc, "The Consent Manager issues and validates authorization artifacts carrying identifiers and approved field scope. College A verifies signed claims and checks live grant status before returning data. Signed JWTs provide integrity/authenticity, not confidentiality; transport security is separately required.")
heading(doc, "3.3 ECDH and Authenticated Encryption", 2)
para(doc, "Both college codebases include elliptic-curve key-pair generation, ECDH shared-secret derivation, and AES/GCM/NoPadding using a 12-byte random IV and a 128-bit authentication tag. The implementation uses the first 16 bytes of the shared secret as AES-128 key material. Production use requires a reviewed KDF, explicit curve selection, context binding, strict input checks, and interoperable key lifecycle management.")
heading(doc, "3.4 Data Minimization and Mapping", 2)
para(doc, "Provider-side extraction uses the Consent Manager-approved field list and a provider mapping registry. The response is a canonical map rather than an unrestricted serialized student entity. College B maps aliases and key capitalization for display without exposing a raw JSON dump in the record modal.")
heading(doc, "3.5 Alternatives and Contribution", 2)
table(doc, ["Approach", "Strength", "Trade-off"], [
    ("Email/file transfer", "Low setup effort", "Weak scope control, revocation, and audit consistency."),
    ("Centralized repository", "Single integration point", "Concentrates sensitive records and requires migration."),
    ("Provider + consent manager", "Provider retains source data; central service coordinates permission.", "Requires key alignment, service availability, schema mapping."),
])
para(doc, "The contribution is a demonstrable modular workflow combining consent lifecycle, field-level authorization, provider-held records, revocation-aware access, and operational interfaces.")

# Chapter 4
page(doc)
heading(doc, "4. SYSTEM ARCHITECTURE AND WORKFLOW")
heading(doc, "4.1 Logical Architecture", 2)
table(doc, ["Node", "Responsibilities", "Local endpoints"], [
    ("Consent Manager", "Organizations/users; consent, grants, audit, bridge, key registration.", "API :8095; UI :3001"),
    ("College A — Provider", "Student records; admin APIs; authorized field extraction.", "API :8081; UI :3002"),
    ("College B — Consumer", "Requests/retrieval; student inbox, history, approval, rejection, revocation.", "API :8082; UI :3003"),
])
para(doc, "Request flow: College B request → Consent Manager lifecycle → student decision → scoped grant and signed claim → College A live grant validation and field extraction → response to College B → consumer verification/view.")
heading(doc, "4.2 End-to-End Workflow", 2)
for x in [
    "College B selects provider, data principal, purpose, and requested academic fields.",
    "The Consent Manager records the request and makes it available to the student workflow.",
    "The student approves a subset of fields or rejects the request.",
    "On approval, the Consent Manager records the decision and creates a grant with approved scope.",
    "The consumer submits the authorized access artifact to the provider endpoint.",
    "College A validates signature/claims and grant identity, then asks the Consent Manager for current grant state.",
    "If valid, the provider locates the student and extracts only supported approved fields.",
    "College B displays mapped values and status; request/audit records support administration.",
    "A revoked or expired grant is denied after live validation.",
]:
    number(doc, x)
heading(doc, "4.3 Trust Artifacts", 2)
table(doc, ["Artifact", "Purpose", "Handling"], [
    ("Login token", "Authenticate portal user and apply role restrictions.", "Not data-access authorization."),
    ("Signed service assertion", "Authenticate college service calls to consent bridge.", "Register/rotate keys consistently."),
    ("Scoped access claim/grant", "Authorize provider request for approved fields.", "Verify signature, identifiers, and active grant."),
])
heading(doc, "4.4 Security and Failure Behavior", 2)
for x in [
    "Role checks partition Super Admin, organization admin, student, and institutional operations.",
    "Provider checks signed claims, grant ID, data principal, and live grant state; empty/invalid scope is denied.",
    "Bridge calls use signed college assertions and registered keys; expired overlap can cause authorization errors.",
    "Trusted-provider URL validation is present; production still needs network egress controls and TLS.",
    "Health endpoints report process health only, not data correctness or dependency readiness.",
]:
    bullet(doc, x)
heading(doc, "4.5 Deployment", 2)
para(doc, "Three Spring Boot backends and three browser frontends are locally orchestrated by start_all.ps1. PostgreSQL is used through Spring Data JPA. College key directories were configured explicitly to avoid different working directories selecting different RSA key material. Production keys must be kept outside source control and supplied through managed secrets or a key service.")

# Chapter 5
page(doc)
heading(doc, "5. DATABASE DESIGN AND DATA MODEL")
heading(doc, "5.1 Persistence Approach", 2)
para(doc, "Backend entities are mapped through JPA and configured for PostgreSQL. The Consent Manager owns governance records; each college owns its local student/admin records. The Consent Manager is not the academic source of truth.")
heading(doc, "5.2 Principal Entities", 2)
table(doc, ["Service", "Entity/table", "Purpose"], [
    ("Consent Manager", "organizations", "Institution registry and metadata."),
    ("Consent Manager", "users", "User identities and roles."),
    ("Consent Manager", "consent_requests", "Principal, recipient, purpose, requested fields, status."),
    ("Consent Manager", "consents", "Decision, approved fields, lifecycle state."),
    ("Consent Manager", "access_grants", "Provider authorization scope and lifecycle."),
    ("Consent Manager", "data_requests", "Consumer request/retrieval state."),
    ("Consent Manager", "audit_logs", "Security and lifecycle event records."),
    ("Consent Manager", "consumed_assertions", "Assertion replay/lifecycle tracking."),
    ("College A", "students; college_a_admins", "Provider academic data and administrator accounts."),
    ("College B", "students; college_b_admins", "Consumer-side student and administrator accounts."),
])
heading(doc, "5.3 Relationships and Governance", 2)
for x in [
    "An organization can have multiple users; administrative access is role-scoped.",
    "A request identifies the data principal and recipient and contains purpose and requested fields.",
    "A consent decision captures approved fields; the resulting grant is constrained to that scope.",
    "Provider disclosure is allowed only while the grant is active according to the Consent Manager.",
    "Production requires retention rules, encrypted backups, least-privilege DB access, and safe logging.",
]:
    bullet(doc, x)
para(doc, "Exact database credentials and real student records are intentionally omitted.")

# Chapter 6
page(doc)
heading(doc, "6. IMPLEMENTATION, TESTING, AND RESULTS")
heading(doc, "6.1 Technology Stack", 2)
table(doc, ["Layer", "Repository implementation"], [
    ("Backend", "Java 17; Spring Boot, Web, Security, Data JPA, Bean Validation."),
    ("Token handling", "JJWT 0.12.5 declared; RSA-signed service/access claims."),
    ("Persistence", "PostgreSQL JDBC driver and JPA entities."),
    ("Frontend", "Browser-based JavaScript portals with shared CSS/HTML assets."),
    ("Build/tests", "Maven, JUnit/Spring test dependencies, Surefire reports."),
    ("Orchestration", "Windows PowerShell multi-service startup script."),
])
heading(doc, "6.2 Test Scorecard", 2)
table(doc, ["Service", "Tests", "Failures", "Errors", "Skipped", "Result"], [
    ("Consent Manager", "26", "0", "0", "0", "PASS"),
    ("College A", "42", "0", "0", "0", "PASS"),
    ("College B", "28", "0", "0", "0", "PASS"),
    ("Total", "96", "0", "0", "0", "PASS"),
])
para(doc, "Source: backend Maven Surefire report files present in each module at report preparation. This is a test-case count, not a performance benchmark or production service-level objective.")
heading(doc, "6.3 Verified Runtime Outputs", 2)
table(doc, ["Check", "Observed result", "Interpretation"], [
    ("GET 127.0.0.1:8095/health", "HTTP 200", "Consent Manager health endpoint responded."),
    ("GET 127.0.0.1:8081/health", "HTTP 200", "College A health endpoint responded."),
    ("GET 127.0.0.1:8082/health", "HTTP 200", "College B health endpoint responded."),
    ("Backend test reports", "96 passed; 0 failures/errors/skips", "All recorded module totals were green."),
])
para(doc, "These are point-in-time local checks, not continuous availability measurements. Protected routes require authentication and were not exhaustively smoke-tested during report preparation; the report does not claim that every endpoint was verified live.")
heading(doc, "6.4 Regression Work Included", 2)
for x in [
    "College B student consent workflow supports inbox/history, field-selective approval, rejection, and revocation.",
    "Consent bridge services recover from expired/outdated assertion-key registration; focused regression tests were run.",
    "College A/B record views map provider payload aliases and omit raw JSON/print-dossier controls.",
    "Retrieval navigation waits for the detail modal to close before routing to records.",
    "Bulk-registration samples use college-specific headers and fictional example.org addresses.",
]:
    bullet(doc, x)
heading(doc, "6.5 Interface Captures", 2)
para(doc, "The following repository-provided portal captures are interface references. Dashboard counts and names are illustrative UI content, not runtime measurements or test results.")
for title, filename in [
    ("Figure 1. Consent Manager interface (illustrative repository capture)", "cm-full-height.png"),
    ("Figure 2. College A provider interface (illustrative repository capture)", "col-a-full-height.png"),
    ("Figure 3. College B consumer interface (illustrative repository capture)", "col-b-full-height.png"),
]:
    page(doc)
    para(doc, title, WD_ALIGN_PARAGRAPH.CENTER)
    image = ROOT / "screenshots" / filename
    if image.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(image), width=Inches(6.15))
    else:
        para(doc, "Screenshot asset not found when the report was generated.", italic=True)

# Chapter 7
page(doc)
heading(doc, "7. USER MANUAL AND OPERATIONS")
heading(doc, "7.1 Prerequisites", 2)
for x in [
    "Java 17 and Maven for backend build/test operations.",
    "PostgreSQL and module configuration suitable for the local environment.",
    "Windows PowerShell for the supplied local startup script.",
    "Institution-specific credentials and signing keys; do not reuse sample/default passwords in deployment.",
]:
    bullet(doc, x)
heading(doc, "7.2 Start the Local System", 2)
for x in [
    "Open PowerShell in the repository root and review commands/configuration in start_all.ps1.",
    "Run .\\start_all.ps1 and keep process windows/logs available for diagnostics.",
    "Check health endpoints on ports 8095, 8081, and 8082; portals use ports 3001, 3002, and 3003.",
    "Use service-specific user accounts. After restart/key rotation, sign out and authenticate again if the session is stale.",
]:
    number(doc, x)
table(doc, ["Component", "Frontend", "Backend health"], [
    ("Consent Manager", "http://127.0.0.1:3001", "http://127.0.0.1:8095/health"),
    ("College A", "http://127.0.0.1:3002", "http://127.0.0.1:8081/health"),
    ("College B", "http://127.0.0.1:3003", "http://127.0.0.1:8082/health"),
])
heading(doc, "7.3 Student Consent Flow", 2)
for x in [
    "Sign in and open the consent inbox or pending-requests view.",
    "Review requester, purpose, data principal, fields, and status.",
    "Approve only necessary fields or reject; confirm the decision in consent history.",
    "Revoke active consent when access should end; the provider checks current grant status.",
]:
    number(doc, x)
heading(doc, "7.4 Consumer Retrieval Flow", 2)
for x in [
    "Sign in as an authorized College B operator and open the request workflow.",
    "Select a registered provider and enter student ID, purpose, and requested fields.",
    "Wait for student decision and active grant status before retrieval.",
    "Review mapped values/status and use the records page for follow-up.",
]:
    number(doc, x)
heading(doc, "7.5 Bulk Registration", 2)
para(doc, "Use samples/college_a_students_sample.csv with headers studentId,name,email,program,cgpa and samples/college_b_students_sample.csv with studentId,name,email,department,cgpa. These files contain fictional example.org addresses. Follow the import screen’s exact field requirements.")
heading(doc, "7.6 Troubleshooting", 2)
table(doc, ["Symptom", "Action"], [
    ("Health endpoint unavailable", "Check process, port, startup logs, DB connectivity, and port conflicts."),
    ("401/403", "Check login, role, route permissions, and correct service identity; do not bypass authentication."),
    ("Consent bridge stale key ID", "Check assertion registration and configured key directory; re-register/rotate with the supported flow."),
    ("Approved request but denied retrieval", "Check approved scope, grant ID/claim match, active grant, and provider principal mapping."),
    ("Missing/displayed-as-dash fields", "Check canonical aliases, mapping registry, approval scope, and source record values."),
    ("Stale modal/session", "Reload after authentication and allow modal close before navigation."),
])

# Chapter 8
heading(doc, "8. CONCLUSION, LIMITATIONS, AND FUTURE WORK")
heading(doc, "8.1 Conclusion", 2)
para(doc, "The project delivers a three-service academic credential exchange prototype that places consent and approved-field scope at the center of retrieval. The Consent Manager manages request/grant lifecycle, College A remains the source of academic records, and College B provides consumer and student workflows. Backend tests and point-in-time health checks provide evidence that core modules run and recorded suites pass.")
heading(doc, "8.2 Limitations", 2)
for x in [
    "Local-development prototype; no production identity proofing, deployment security review, disaster-recovery exercise, or independent penetration test is claimed.",
    "Live checks cover health endpoints; exhaustive protected-route and full browser-to-provider-to-consumer verification is not claimed.",
    "ECDH/AES utility uses a direct shared-secret slice for AES key material and needs a reviewed KDF/protocol before production.",
    "Key registration depends on consistent key identifiers and configured directories; stale keys can interrupt bridge communication.",
    "Performance, concurrency, retention, usability, and cross-institution benchmarks have not been established.",
    "CSV ingestion needs further validation for quoting, malformed input, and arbitrary external files.",
]:
    bullet(doc, x)
heading(doc, "8.3 Future Enhancements", 2)
for x in [
    "Adopt an approved KDF, protocol versioning, key confirmation, and managed key rotation.",
    "Deploy TLS, managed secrets, strict CORS, network egress controls, rate limits, secure token policy, and monitoring.",
    "Add browser-level end-to-end tests for request, decision, grant, retrieval, field filtering, and revocation.",
    "Add schema versioning and standard credential formats across institution registries.",
    "Define retention/deletion policies and test backup/restore and operational recovery.",
    "Run repeatable load, concurrency, and resilience tests.",
]:
    bullet(doc, x)

page(doc)
heading(doc, "REFERENCES")
for ref in [
    "[1] NITI Aayog, “Data Empowerment and Protection Architecture (DEPA),” framework materials. https://www.niti.gov.in/ (accessed 06 Nov 2026).",
    "[2] IETF, RFC 7519, “JSON Web Token (JWT),” May 2015. https://www.rfc-editor.org/rfc/rfc7519",
    "[3] IETF, RFC 8725, “JSON Web Token Best Current Practices,” February 2020. https://www.rfc-editor.org/rfc/rfc8725",
    "[4] NIST SP 800-56A Rev. 3, “Pair-Wise Key-Establishment Schemes Using Discrete Logarithm Cryptography,” 2018. https://csrc.nist.gov/pubs/sp/800/56/a/r3/final",
    "[5] NIST SP 800-38D, “Galois/Counter Mode (GCM) and GMAC,” 2007. https://csrc.nist.gov/pubs/sp/800/38/d/final",
    "[6] Spring Boot Reference Documentation. https://docs.spring.io/spring-boot/reference/",
    "[7] Spring Security Reference. https://docs.spring.io/spring-security/reference/",
    "[8] Project source: Consent Manager, College A, College B, start_all.ps1, and sample CSV files; reviewed 06 Nov 2026.",
    "[9] Backend Maven Surefire reports in each service module; test totals transcribed 06 Nov 2026.",
]:
    para(doc, ref)

page(doc)
heading(doc, "APPENDIX A: MODULE DIRECTORY")
table(doc, ["Path", "Purpose"], [
    ("consent-manager/backend", "Consent, organization, user, grant, audit, and bridge APIs."),
    ("consent-manager/frontend", "Consent Manager administration and user portal."),
    ("college-a/backend", "Provider authentication, student data, consent bridge, authorized access."),
    ("college-a/frontend", "College A registrar and student pages."),
    ("college-b/backend", "Consumer request/retrieval and student consent workflows."),
    ("college-b/frontend", "College B administration, request, records, and student pages."),
    ("samples/college_a_students_sample.csv", "Fictional College A registration example."),
    ("samples/college_b_students_sample.csv", "Fictional College B registration example."),
    ("start_all.ps1", "Local multi-service startup orchestration."),
])
heading(doc, "APPENDIX B: SELECTED API GROUPS", 1)
table(doc, ["Service", "API groups"], [
    ("Consent Manager", "/health; /api/auth; /api/bridge; /api/consents; /api/access-grants; /api/admin; /api/org-admin; /api/audit."),
    ("College A", "/health; /api/auth; /api/students; /api/student; /api/consumer; /api/data/access; provider onboarding."),
    ("College B", "/health; /api/auth; /api/students; /api/student; /api/consumer; /api/data/access; provider onboarding."),
])
para(doc, "Exact methods, schemas, and authorization rules are defined by the controller and security configuration classes; this summary is not a substitute for the API contract.")
heading(doc, "APPENDIX C: VERIFICATION SNAPSHOT", 1)
para(doc, "Backend Surefire summary: Consent Manager 26/26, College A 42/42, College B 28/28. Combined: 96 tests, 0 failures, 0 errors, 0 skipped. The three health endpoints returned HTTP 200 at report preparation. No secrets, tokens, private keys, real student records, or default credentials are included.")
para(doc, "END OF REPORT", WD_ALIGN_PARAGRAPH.CENTER)

doc.core_properties.title = "Consent-Centric Academic Credential Exchange Network — Project Report"
doc.core_properties.subject = "DEPA-inspired academic consent and credential sharing system"
doc.core_properties.author = "ANITS CSE Project Team"
doc.core_properties.keywords = "DEPA, consent, academic credentials, College A, College B"
doc.save(DOCX)
print(f"Created {DOCX} ({DOCX.stat().st_size} bytes)")
