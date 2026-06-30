# Submission Manifest

Date: 2026-06-30

Archive: `lab24_submission_medviet.zip`

## Included

- `src/`
- `tests/`
- `policies/`
- `data/processed/`
- `compliance_checklist.md`
- `reports/`
- `requirements.txt`
- `scripts/generate_data.py`
- `.github/hooks/pre-commit`
- `docker-compose.yml`
- `prometheus.yml`
- `prometheus_alert_rules.yml`

## Excluded

- `data/raw/`
- `.vault_key`
- `.git/`
- `.venv/`
- `__pycache__/`
- real credentials

## Verification

- Raw patient data is excluded from the submission archive.
- Local vault keys are excluded from the submission archive.
- Security and validation evidence are included in `reports/`.
