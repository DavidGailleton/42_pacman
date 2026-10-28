# Project management

How the Pac-Man project was planned, followed and delivered by
**dgaillet** and **mteriier**.

**Status: finished** (2026-10-28). All features of the subject are
implemented and merged into `main`.

| Document | Content |
| -------- | ------- |
| [timeline.md](timeline.md) | Epics, Kanban board and timeline of the project |
| [progress_tracking.md](progress_tracking.md) | Actual progress compared to the plan, issue by issue |
| [risk_analysis.md](risk_analysis.md) | Risks identified, their impact and how we mitigated them |
| [team_organization.md](team_organization.md) | Who did what, git workflow, decisions, blocking points |

The acceptance test plan is covered by the unit tests in
[`tests/test_acceptance_configs.py`](../tests/test_acceptance_configs.py)
and the fixture files in [`tests/test_configs/`](../tests/test_configs/).

## Tools

- **GitHub Issues**: one issue per task, grouped into 4 epics.
- **GitHub Projects (Kanban)**: `Todo` → `In progress` → `In review` → `Done`.
- **Pull Requests**: every feature branch is merged into `main` through a PR.
- **Makefile**: `make lint` and `make test` as the quality gate before a merge.
