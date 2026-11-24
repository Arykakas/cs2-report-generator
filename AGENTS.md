
# Project Context: CS2 Match Analyzer

## Project overview
A local Counter-Strike 2 demo analysis application.
Users upload demo files and receive match analysis
and performance reports.

## Architecture
- Describe the main application entry point.
- Describe the analysis pipeline.
- Describe report generation.
- Describe how data flows between modules.

## Important modules
- app.py: Main application entry point.
- pipeline.py: Demo analysis pipeline.
- report.py: Report generation.
- analysis_wrapper.py: Analysis integration.

Verify these responsibilities against the actual code
before relying on them.

## Development requirements
- Preserve existing application architecture.
- Maintain compatibility between modules.
- Keep UI and analysis logic separated.
- Preserve existing report formats.
- Avoid unnecessary dependencies.
- Read existing code before making changes.
- Prefer minimal targeted edits.
- Do not repeatedly retry failed edits.
- Verify modifications using Git diff.
- Run relevant tests before declaring completion.
- Never claim a task is complete without verification.
- Protect existing uncommitted user changes.
- Keep project documentation and session handoff information accurate.

## Before modifying the project
- Read relevant existing implementations.
- Check callers and dependencies.
- Identify the canonical file to modify.
- Never assume a backup or experimental file
  is the active implementation.

## Persistent Project Memory and Session Handoff

The `.project-context/` directory contains the persistent development memory for this repository.

### Required reading at session start

Before starting work:

1. Read `.project-context/PROJECT_STATE.md`.
2. Read `.project-context/SESSION_HANDOFF.md`.
3. Read `.project-context/DECISIONS_AND_ISSUES.md`.
4. Read the authoritative task checklist `REPORT_2_0_MODULE_1_TASKS.md`.
5. Verify the current Git status before editing.
6. Treat the task checklist as authoritative for task completion status.

Do not assume previous AI summaries are accurate without verification.

### Required handoff updates

After completing each meaningful task or subtask:

1. Update `.project-context/SESSION_HANDOFF.md`.
2. Record what was completed and what remains.
3. Record files actually modified.
4. Record tests executed and their actual results.
5. Record blockers, unresolved questions, and failed approaches.
6. Specify the exact next action and files that should be inspected first.
7. Do not mark work complete unless it has been verified.

When project status materially changes:

1. Update `.project-context/PROJECT_STATE.md`.
2. Keep completed, in-progress, and remaining tasks accurate.
3. Distinguish completed design decisions from implementation and verification status.

When a decision or blocker changes:

1. Update `.project-context/DECISIONS_AND_ISSUES.md`.
2. Record the decision, its reasoning, and any unresolved uncertainty.

Before ending a work session:

1. Update `SESSION_HANDOFF.md`, even if the current task is unfinished.
2. Leave a clear continuation point so a fresh agent session can resume without reconstructing the conversation.
3. Include the exact next action, relevant files, current blockers, and verification status.

### Accuracy and safety

- Never invent completed work, test results, file modifications, or verification.
- Clearly label assumptions and unverified workarounds.
- Do not overwrite or discard existing user changes.
- Keep updates concise and factual.
- Inspect the resulting Git diff after editing.
- Do not modify unrelated files.
