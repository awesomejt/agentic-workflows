# Software development loop

Run the `software-development` workflow for `<TASK_REF>` with objective
`<OBJECTIVE>` and acceptance criteria `<ACCEPTANCE_CRITERIA>`.

Use the reset-safe protocol and `.agents/loop/<RUN_ID>/`. Start each stage in a
fresh context. The expected progression is orchestration, task scoping, planning,
design challenge, focused implementation, static validation, behavioral testing,
independent review, documentation, optional authorized commit, and task closeout.

Route a failed validation, test, or review pass back to a focused implementation
pass. Preserve exact commands and findings in the handoff. Do not close merely
because the implementation exists; all required gates need direct evidence.
