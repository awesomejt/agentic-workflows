# Project Template Catalog

The catalog pins the three existing starter repositories by revision and records
which files should become reusable bundles. It deliberately does not copy
repository task state, chat logs, or machine-specific configuration.

The normalization boundary is:

- common behavior and skills come from `common/`;
- engineering, course, or project-domain instructions stay in their template;
- generated projects receive fresh `MEMORY.md`, `TODO.md`, `status.yaml`, and AWB
  project configuration;
- upstream starter repositories remain the review source until a normalized
  bundle reaches `ready` status.

The next implementation step is a `workflowctl template render` command that
materializes a selected bundle with placeholder validation. Until then, use the
catalog as the revision-pinned migration plan rather than copying files by hand.
