# MedViet Operational Compliance Evidence

Date: 2026-06-30

## Data Localization

- Primary environment: Vietnam region only for patient data storage.
- Backup policy: backups inherit the same Vietnam-only residency requirement.
- Technical enforcement: OPA denies restricted data export when `destination_country != "VN"`.
- Transfer register: cross-border attempts must be recorded with user, role, action, dataset, destination country, decision, and timestamp.

## Consent Management

- Consent is required before data is used for AI training.
- Consent record fields: `patient_id`, `consent_scope`, `policy_version`, `granted_at`, `withdrawn_at`, `source_channel`, and `operator`.
- Withdrawal workflow: mark consent as withdrawn, enqueue patient id for training dataset refresh, remove direct identifiers from downstream datasets, and retain an audit event.
- AI training guardrail: only anonymized records with active consent are eligible for training exports.

## Breach Notification - 72 Hours

- Incident owner: Security Team.
- Escalation contacts: DPO, Platform Lead, Legal/Compliance.
- Severity P1 examples: confirmed raw PII leak, restricted data export outside Vietnam, compromised admin credential.
- Required timeline: triage immediately, contain within 24 hours, notify competent authority within 72 hours when legally required.
- Evidence source: `reports/audit_events.jsonl`, OPA decisions, Prometheus alerts, Bandit/TruffleHog scan reports.

## DPO

- Lab DPO contact: `dpo@medviet.example.vn`.
- Production action: replace the lab mailbox with the appointed organization's real DPO mailbox before go-live.
- DPO responsibilities: privacy review, breach notification coordination, consent process oversight, and periodic access review.

## Key Management

- Lab implementation: local envelope encryption with AES-256-GCM in `src/encryption/vault.py`.
- Production requirement: store KEK in HSM/KMS, rotate KEK at least annually, rotate immediately on suspected compromise, and deny direct plaintext key export.
- Operational rule: `.vault_key` is local-only and excluded by `.gitignore`; it must not be committed or submitted.

## Audit Logging

- API authorization events are appended as JSON lines to `reports/audit_events.jsonl`.
- Minimum fields: timestamp, user, role, resource, action, decision, status code, and denial reason when applicable.
- Retention target: append-only storage for incident response and compliance review.

## Pre-Commit Secret Blocking Evidence

- Hook template: `.github/hooks/pre-commit`.
- The hook runs `git secrets --pre_commit_hook`, `bandit -r src/ -ll -q`, and `pip-audit --desc on`.
- Fake credential test procedure: create a temporary file containing an AWS-style fake secret, stage it, run the hook, verify the commit is blocked, then remove the temporary file before submission.
- Submission state: no fake credential file is present in the repo or archive; TruffleHog reports zero verified and zero unverified secrets.
