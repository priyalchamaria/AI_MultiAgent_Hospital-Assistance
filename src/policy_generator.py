from __future__ import annotations

from pathlib import Path


DISCLAIMER = "Synthetic academic policy. This document is generated for internship project demonstration only."


POLICIES = {
    "visitor_policy.txt": {
        "title": "Visitor Policy",
        "id": "HOSP-POL-001",
        "purpose": "Define safe visitor access while protecting patient rest, privacy, and clinical operations.",
        "scope": "Applies to inpatient units, outpatient treatment areas, emergency waiting zones, and visitor registration desks.",
        "responsibilities": "Security verifies visitor identity. Nurses may limit visits based on clinical need. Unit managers review exceptions.",
        "procedure": "General visiting hours are 10:00 AM to 7:00 PM. A maximum of two visitors may be present per patient unless an exception is approved. Visitors must wear identification badges and follow infection-control instructions.",
        "exceptions": "End-of-life care, pediatric guardians, disability support persons, and approved interpreters may receive extended access.",
        "escalation": "Disruptive visitors are escalated to the charge nurse and security. Safety threats are escalated immediately to hospital security leadership.",
        "review": "2027-01-15",
    },
    "admission_policy.txt": {
        "title": "Admission Policy",
        "id": "HOSP-POL-002",
        "purpose": "Ensure every admission has accurate identity, clinical, insurance, and consent documentation.",
        "scope": "Applies to elective, urgent, and emergency admissions.",
        "responsibilities": "Registration staff collect demographics and insurance details. Clinical staff verify admission type, initial diagnosis, allergies, and care priority.",
        "procedure": "At admission, staff confirm patient identity using two identifiers, capture demographic information, record admission type, assign room when available, and notify the responsible clinician.",
        "exceptions": "Emergency stabilization may occur before full registration when delaying care would create risk.",
        "escalation": "Identity conflicts, missing consent, or unsafe room placement must be escalated to the admission supervisor.",
        "review": "2027-02-01",
    },
    "discharge_policy.txt": {
        "title": "Discharge Policy",
        "id": "HOSP-POL-003",
        "purpose": "Ensure patients leave with safe instructions, medication guidance, and follow-up planning.",
        "scope": "Applies to all discharged inpatients and observation patients.",
        "responsibilities": "Clinicians complete discharge summaries. Nurses review instructions. Case management supports high-risk discharge needs.",
        "procedure": "Discharge planning begins at admission. Before discharge, staff verify diagnosis, medication changes, pending tests, follow-up appointments, transport, and home-care needs.",
        "exceptions": "Patients leaving against medical advice must receive risk counseling and available written instructions.",
        "escalation": "If a patient lacks a safe home environment, medication access, or required equipment, staff must escalate to case management before discharge.",
        "review": "2027-03-01",
    },
    "medication_policy.txt": {
        "title": "Medication Administration Policy",
        "id": "HOSP-POL-004",
        "purpose": "Reduce medication errors through verification, reconciliation, and documentation.",
        "scope": "Applies to ordering, dispensing, administering, reconciling, and documenting medications.",
        "responsibilities": "Prescribers enter complete orders. Pharmacy validates orders. Nurses confirm patient identity and document administration.",
        "procedure": "Staff verify patient, medication, dose, route, time, indication, allergies, and documentation before administration. High-alert medications require independent double-checks.",
        "exceptions": "Emergency medication administration may proceed under emergency protocols with documentation completed as soon as possible.",
        "escalation": "Medication discrepancies, omitted doses, adverse reactions, or unclear orders must be escalated to the prescriber and pharmacy.",
        "review": "2027-04-01",
    },
    "privacy_policy.txt": {
        "title": "Patient Privacy Policy",
        "id": "HOSP-POL-005",
        "purpose": "Protect patient confidentiality and ensure access to information is based on legitimate work need.",
        "scope": "Applies to electronic records, printed records, verbal communication, images, billing data, and audit logs.",
        "responsibilities": "All staff protect credentials and access only records needed for treatment, billing, operations, compliance, or approved review.",
        "procedure": "Staff must lock unattended workstations, avoid discussing patient details in public areas, and dispose of printed records in secure shredding bins.",
        "exceptions": "Disclosure may occur when required by law, patient authorization, or approved emergency response.",
        "escalation": "Suspected privacy incidents must be reported to the compliance office within 24 hours.",
        "review": "2027-05-01",
    },
    "emergency_response_policy.txt": {
        "title": "Emergency Response Policy",
        "id": "HOSP-POL-006",
        "purpose": "Provide a coordinated response to clinical emergencies, facility threats, and mass-casualty events.",
        "scope": "Applies to all hospital departments, contractors, and visitors during emergency events.",
        "responsibilities": "Staff activate the correct emergency code, protect patients, follow command instructions, and document actions after stabilization.",
        "procedure": "Emergency response begins with immediate safety assessment, activation of the emergency code, notification of the response team, patient protection, and event documentation.",
        "exceptions": "Departments may adapt procedures when local conditions make the standard route unsafe.",
        "escalation": "Uncontrolled hazards, mass-casualty incidents, or failed communication systems escalate to the incident command leader.",
        "review": "2027-06-01",
    },
    "infection_control_policy.txt": {
        "title": "Infection Control Policy",
        "id": "HOSP-POL-007",
        "purpose": "Minimize healthcare-associated infections among patients, visitors, and staff.",
        "scope": "Applies to patient-care areas, shared equipment, isolation rooms, procedure areas, and staff workspaces.",
        "responsibilities": "All staff perform hand hygiene. Department leaders monitor compliance. Infection prevention staff audit and coach teams.",
        "procedure": "Hand hygiene is required before and after patient contact, after exposure to bodily fluids, after removing gloves, and before clean procedures. Shared equipment must be disinfected between patients.",
        "exceptions": "Emergency care may begin before full isolation setup if delay would endanger the patient.",
        "escalation": "Suspected outbreaks or repeated non-compliance must be escalated to infection prevention leadership.",
        "review": "2027-07-01",
    },
    "billing_insurance_policy.txt": {
        "title": "Billing and Insurance Policy",
        "id": "HOSP-POL-008",
        "purpose": "Support accurate billing, insurance documentation, and transparent patient communication.",
        "scope": "Applies to registration, coding, billing, insurance verification, and patient financial counseling.",
        "responsibilities": "Billing staff validate payer information. Clinical teams document services. Finance teams audit unusual billing patterns.",
        "procedure": "Insurance provider, admission type, services, billing amount, and discharge date must be documented accurately. Corrections require a traceable reason.",
        "exceptions": "Urgent care must not be delayed while insurance details are being verified.",
        "escalation": "Coverage disputes, suspected billing errors, or repeated documentation gaps must be escalated to the billing supervisor.",
        "review": "2027-08-01",
    },
    "incident_reporting_policy.txt": {
        "title": "Incident Reporting Policy",
        "id": "HOSP-POL-009",
        "purpose": "Ensure safety events, near misses, privacy concerns, and operational incidents are reported and reviewed.",
        "scope": "Applies to clinical incidents, visitor incidents, medication events, falls, equipment failures, and privacy concerns.",
        "responsibilities": "Any staff member who observes an incident must report it. Managers review reports and assign corrective actions.",
        "procedure": "Incidents should be entered in the incident reporting system before the end of the shift. Reports must include date, location, involved parties, description, immediate actions, and witnesses.",
        "exceptions": "Immediate patient safety actions should occur before report entry.",
        "escalation": "Severe harm, legal risk, media risk, or repeated safety events escalate to risk management and department leadership.",
        "review": "2027-09-01",
    },
    "medical_record_access_policy.txt": {
        "title": "Medical Record Access Policy",
        "id": "HOSP-POL-010",
        "purpose": "Define authorized access, release, and audit practices for medical records.",
        "scope": "Applies to electronic health records, archived charts, scanned documents, and release-of-information workflows.",
        "responsibilities": "Health information management validates releases. Staff access records only for assigned work. Compliance reviews audit exceptions.",
        "procedure": "Requests for medical records require identity verification and authorization unless access is for treatment, payment, operations, or required law. Audit logs are reviewed for inappropriate access.",
        "exceptions": "Emergency access is permitted when required for immediate patient care and must be reviewed afterward.",
        "escalation": "Unauthorized access, suspicious audit activity, or disputed release requests must be escalated to compliance.",
        "review": "2027-10-01",
    },
}


def ensure_policy_documents(policy_dir: Path) -> list[Path]:
    policy_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, fields in POLICIES.items():
        path = policy_dir / filename
        content = f"""Policy Title: {fields['title']}
Policy ID: {fields['id']}
Notice: {DISCLAIMER}

Purpose:
{fields['purpose']}

Scope:
{fields['scope']}

Responsibilities:
{fields['responsibilities']}

Procedure:
{fields['procedure']}

Exceptions:
{fields['exceptions']}

Escalation Process:
{fields['escalation']}

Review Date:
{fields['review']}
"""
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths
