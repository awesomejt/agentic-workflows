# workflowctl

`workflowctl` validates, renders, compares, deploys, and audits configuration
from the repository root.

Run it without installation through the repository wrapper:

```bash
bin/workflowctl validate
bin/workflowctl inventory
bin/workflowctl render --target workstation
bin/workflowctl diff --target workstation
bin/workflowctl deploy --target workstation --dry-run
bin/workflowctl doctor --target workstation
```

Use `--home` with `diff`, `deploy`, `audit`, or `doctor` to redirect all
home-relative destinations and state to an isolated test home.

Live deployment uses copy-with-backup unless the target or `--mode` selects
symlinks. A state manifest is written outside the repository and can be checked
with `workflowctl audit`.
