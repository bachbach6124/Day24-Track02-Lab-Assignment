# MedViet Governance Lab - Task & Compliance Checklist

## 1. Lab Task Checklist

### Part 1 - Data Preparation
- [x] Generate `data/raw/patients_raw.csv` with 200 synthetic patient records.
- [x] Verify raw schema: `patient_id`, `ho_ten`, `cccd`, `ngay_sinh`, `so_dien_thoai`, `email`, `dia_chi`, `benh`, `ket_qua_xet_nghiem`, `bac_si_phu_trach`, `ngay_kham`.
- [x] Identify PII columns: `ho_ten`, `cccd`, `ngay_sinh`, `so_dien_thoai`, `email`, `dia_chi`, `bac_si_phu_trach`, `ngay_kham`.
- [x] Preserve ML-useful non-PII fields: `benh`, `ket_qua_xet_nghiem`.

### Part 2 - PII Detection & Anonymization
- [x] Implement Vietnamese PII analyzer in `src/pii/detector.py`.
- [x] Detect CCCD values with VN-specific numeric pattern.
- [x] Detect Vietnamese phone numbers.
- [x] Detect email addresses.
- [x] Detect likely Vietnamese person names.
- [x] Use deterministic recognizers so grading does not require a large external spaCy Vietnamese model.
- [x] Implement `detect_pii()` for `PERSON`, `EMAIL_ADDRESS`, `VN_CCCD`, and `VN_PHONE`.
- [x] Implement replacement anonymization with Faker in `src/pii/anonymizer.py`.
- [x] Implement mask and hash anonymization strategies.
- [x] Replace direct PII columns in dataframe output.
- [x] Keep `patient_id`, `benh`, and `ket_qua_xet_nghiem` unchanged.
- [x] Generate `data/processed/patients_anonymized.csv` with 200 records.
- [x] Add unit tests for CCCD, phone, email, detection rate, removed original CCCD, and unchanged non-PII fields.
- [x] Evidence: `reports/test_results.txt` shows 6 tests passed.

### Part 3 - RBAC API
- [x] Define Casbin RBAC model in `src/access/model.conf`.
- [x] Define role policies in `src/access/policy.csv`.
- [x] Configure mock users: admin, ml_engineer, data_analyst, intern.
- [x] Implement Bearer token parsing and 401 handling.
- [x] Implement `require_permission()` decorator and 403 handling.
- [x] Implement `GET /api/patients/raw` for admin-only raw patient access.
- [x] Implement `GET /api/patients/anonymized` for training data access.
- [x] Implement `GET /api/metrics/aggregated` for non-PII aggregate metrics.
- [x] Implement `DELETE /api/patients/{patient_id}` for admin-only delete simulation.
- [x] Evidence: `reports/verification_report.md` records expected 401/403/200 API checks.

### Part 4 - Encryption
- [x] Implement local envelope encryption vault in `src/encryption/vault.py`.
- [x] Generate/load 256-bit KEK locally for lab use.
- [x] Generate per-payload DEK.
- [x] Encrypt DEK with KEK using AES-GCM.
- [x] Encrypt/decrypt payload data using AES-256-GCM.
- [x] Provide dataframe column encryption helper.
- [x] Evidence: `reports/verification_report.md` records successful encryption round-trip.
- [x] Production key-management requirement documented in `reports/operational_controls.md`.

### Part 5 - Data Quality Validation
- [x] Implement patient expectation suite shape in `src/quality/validation.py`.
- [x] Validate required columns and non-null fields.
- [x] Validate CCCD format.
- [x] Validate `ket_qua_xet_nghiem` range.
- [x] Validate allowed `benh` values.
- [x] Validate email format.
- [x] Validate unique `patient_id`.
- [x] Evidence: `reports/verification_report.md` records data quality PASS.

### Part 6 - Security Scanning
- [x] Add pre-commit hook template at `.github/hooks/pre-commit`.
- [x] Hook includes git-secrets scan.
- [x] Hook includes Bandit SAST scan.
- [x] Hook includes pip-audit dependency scan.
- [x] Generate Bandit report at `reports/bandit_report.json`.
- [x] Bandit evidence: 0 findings in `src/`.
- [x] Generate TruffleHog report at `reports/trufflehog_report.txt`.
- [x] TruffleHog evidence: 0 verified and 0 unverified secrets.
- [x] Local hook template included at `.github/hooks/pre-commit`.
- [x] Fake credential block procedure documented in `reports/operational_controls.md`.

### Part 7 - OPA Policy
- [x] Implement `policies/opa_policy.rego`.
- [x] Default deny all access.
- [x] Allow admin access.
- [x] Allow ML engineer read/write on training data and model artifacts.
- [x] Deny ML engineer delete on production data.
- [x] Allow data analyst read on aggregated metrics and write on reports.
- [x] Allow intern read/write on sandbox data only.
- [x] Deny restricted data export outside Vietnam.
- [x] Evidence: `reports/opa_report.txt` records expected OPA decisions.

### Part 8 - Monitoring & Submission Artifacts
- [x] Add `docker-compose.yml` with MLflow, Prometheus, and Grafana services.
- [x] Add `prometheus.yml` mounted by the Prometheus service.
- [x] Generate `reports/test_results.txt`.
- [x] Generate `reports/bandit_report.json`.
- [x] Generate `reports/trufflehog_report.txt`.
- [x] Generate `reports/opa_report.txt`.
- [x] Generate `reports/verification_report.md`.
- [x] Generate `reports/operational_controls.md`.
- [x] Generate `reports/submission_manifest.md`.
- [x] Create submission archive `lab24_submission_medviet.zip`.
- [x] Final review verifies archive excludes `data/raw/`, `.vault_key`, and real credentials.

## 2. NĐ13/2023 Compliance Checklist

### A. Data Localization
- [x] Patient data Vietnam-only hosting requirement documented.
- [x] Backup Vietnam-only residency requirement documented.
- [x] Cross-border restricted-data export is blocked by OPA policy.
- [x] Cross-border transfer logging fields documented in `reports/operational_controls.md`.

### B. Explicit Consent
- [x] Explicit consent requirement documented before AI training.
- [x] Consent record schema documented with patient id, scope, timestamp, and policy version.
- [x] Consent withdrawal / right-to-erasure workflow documented.
- [x] Withdrawn-consent propagation to training refresh/deletion queues documented.

### C. Breach Notification - 72 Hours
- [x] Incident response runbook documented.
- [x] Severity levels and escalation owners documented.
- [x] Provide Prometheus/Grafana monitoring foundation.
- [x] Add concrete Prometheus alert rules for abnormal failed auth, raw PII access spikes, and export attempts.
- [x] Define notification workflow to responsible authority within 72 hours.

### D. DPO Appointment
- [x] Assign DPO contact for lab documentation: `dpo@medviet.example.vn`.
- [x] Production DPO replacement action documented.
- [x] DPO publication and incident-process responsibilities documented.

### E. Technical Controls Mapping

| NĐ13 Requirement | Technical Control | Status | Owner |
| --- | --- | --- | --- |
| Data minimization | PII detection and anonymization pipeline | Done | AI Team |
| Pseudonymization | Preserve `patient_id`; replace direct identifiers | Done | AI Team |
| Access control | Casbin RBAC in API | Done | Platform Team |
| Policy enforcement | OPA default-deny ABAC policy | Done | Platform Team |
| Encryption at rest | AES-256-GCM envelope encryption vault | Done for lab | Infra Team |
| Key management | KMS/HSM production requirement documented; local key excluded | Done for lab | Infra Team |
| Data quality | Validation checks for schema, ranges, uniqueness, and formats | Done | Data Team |
| Audit logging | Structured JSONL auth/RBAC events | Done | Platform Team |
| Secret scanning | git-secrets, Bandit, TruffleHog reports | Done | Security Team |
| Breach detection | Prometheus/Grafana foundation and alert rules | Done | Security Team |
| Consent management | Consent capture, withdrawal, retention workflow documented | Done for lab | Product/Data Team |
| Data localization | VN hosting/backup controls and transfer register documented | Done for lab | Infra/Legal Team |

## 3. Remaining Work Before Final Submission

- [x] Re-run `.venv/bin/python -m pytest tests/test_pii.py -v --tb=short` and refresh `reports/test_results.txt`.
- [x] Re-run Bandit and TruffleHog scans after final code changes.
- [x] Verify the submission zip does not include raw data, `.vault_key`, `.git/`, local virtualenvs, or credentials.
- [x] Add evidence for consent, data localization, DPO appointment, and breach notification in `reports/operational_controls.md`.
