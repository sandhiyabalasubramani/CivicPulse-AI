# CivicPulse AI — Production Readiness Checklist

This checklist separates repository-level checks from deployment checks that require access to the live hosting and database accounts. Do not mark a live check complete based only on a local test run.

## Repository and CI

- [x] Source code, tests, environment template, and architecture documentation are version-controlled.
- [x] Automated pytest workflow is configured in GitHub Actions.
- [ ] Confirm the first GitHub Actions run completes successfully.
- [ ] Review dependency alerts and update dependencies deliberately.
- [ ] Confirm no real credentials, database exports, or personal complaint data are committed.

## Deployment configuration

### Streamlit frontend

- [ ] Confirm the Streamlit Community Cloud app points to this repository and the intended branch.
- [ ] Configure `API_URL` in Streamlit secrets to the deployed FastAPI base URL.
- [ ] Configure any required application secrets only in the hosting provider's secret settings.
- [ ] Submit a test complaint and confirm the returned reference ID can be tracked.

### FastAPI backend

- [ ] Confirm the Render service builds from the intended repository and branch.
- [ ] Set `DATABASE_URL` to the production PostgreSQL connection string.
- [ ] Set a unique, high-entropy `ADMIN_API_KEY`; never reuse the example value.
- [ ] Verify `/health` and `/docs` after deployment.
- [ ] Verify protected status-update routes reject requests with missing or incorrect admin credentials.
- [ ] Confirm logs do not expose credentials, complaint contact details, or internal exception traces.

### PostgreSQL and data safety

- [ ] Confirm production database SSL is enabled and connection settings are correct.
- [ ] Verify schema initialization/migrations against a non-production database first.
- [ ] Confirm automated backups and a tested restore procedure are available for the chosen database plan.
- [ ] Confirm retention, access, and deletion policies are appropriate for personal complaint data.
- [ ] Verify KPI totals agree with complaint records and status-history entries after a status transition.

## End-to-end smoke test

Run this after each deployment, using a clearly identified test record and no real personal data.

1. Open the public Streamlit app and submit a test complaint.
2. Confirm a reference ID is returned and the record appears in tracking.
3. Confirm category, priority, department, and SLA are populated plausibly.
4. Open admin operations and verify unauthorized status changes are rejected.
5. Apply an authorized status update and confirm the audit history records it.
6. Confirm analytics and PDF/CSV exports reflect the same record and status.
7. Delete or clearly close the test record according to the application's data policy.

## Release decision

A release is ready only when the automated CI run is green, the end-to-end smoke test passes, and production secrets, database backups, and access controls have been reviewed. Items that require provider dashboards or production credentials must be checked by the repository owner.
