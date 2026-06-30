# MedViet Governance Verification Report

Date: 2026-06-30

## Automated Tests

- Command: `.venv/bin/python -m pytest tests/test_pii.py -v --tb=short`
- Result: PASS
- Summary: 6 tests passed

## API and RBAC Checks

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| `GET /api/patients/raw as token-bob` | 403 | 403 | PASS |
| `GET /api/patients/raw as token-alice` | 200 | 200 | PASS |
| `DELETE /api/patients/abc123 as token-bob` | 403 | 403 | PASS |
| `GET /api/metrics/aggregated as token-carol` | 200 | 200 | PASS |
| `GET /api/patients/anonymized as token-bob` | 200 | 200 | PASS |
| `GET /api/metrics/aggregated as token-dave` | 403 | 403 | PASS |
| `GET /api/patients/raw without token` | 401 | 401 | PASS |

## Audit Logging Check

- File: `reports/audit_events.jsonl`
- Structured events emitted: 7
- Result: PASS

## Encryption Check

- Round-trip payload: `Nguyen Van A - CCCD: 012345678901`
- Algorithm: `AES-256-GCM`
- Result: PASS

## Data Quality Check

- File: `data/processed/patients_anonymized.csv`
- Rows: 200
- Failed checks: none
- Result: PASS

## OPA Policy Check

- See `reports/opa_report.txt` for admin allow, ML delete deny, and restricted export deny checks.

## Compose/Monitoring Check

- `prometheus.yml` loads `prometheus_alert_rules.yml`.
- Alerts cover repeated authorization denial, raw PII access spike, and restricted export attempt.
