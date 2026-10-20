# Changelog

## 0.2.0 - 2026-10-20

### Added

- JSON campaign import/export and example generation.
- Per-class perception metrics and missing-detection accounting.
- Explicit human review records for critical scenarios.
- REST endpoints for real campaign runs, report retrieval and evidence verification.
- Optional bounded, filesystem-backed report persistence.
- Integration tests for the CLI, HTTP API, persistence and evidence flow.

### Changed

- Reject duplicate, orphaned and misaligned frame data instead of silently truncating it.
- Render dashboard gates through DOM APIs instead of `innerHTML`.
- Bump package version to 0.2.0.

### Security

- Authenticate report retrieval and mutating API operations when `API_TOKEN` is configured.
- Preserve 1,000,000-byte request bounds and add `frame-ancestors 'none'` to the CSP.
