# Content creation loop

Run the `content-creation` workflow for `<TASK_REF>` with deliverable
`<DELIVERABLE>`, audience `<AUDIENCE>`, and acceptance criteria
`<ACCEPTANCE_CRITERIA>`.

Use the reset-safe protocol, the installed `workflows/content-creation.yaml`
stage graph when available, and `.agents/loop/<RUN_ID>/`. Start each stage in a
fresh context. The expected progression is orchestration, task scoping, content
planning, authoritative research, drafting, editing, factual validation,
independent review, and task closeout.

Send unsupported or stale claims back to research and substantive presentation
issues back to editing. Keep sourced facts separate from inference, preserve
source references in concise handoffs, and do not approve content solely because
it reads well.
