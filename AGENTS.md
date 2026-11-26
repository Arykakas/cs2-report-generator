# Project Context: CS2 Match Analyzer

## Shell Environment (WSL / Linux-only) — READ FIRST

This project is edited and run inside WSL (Ubuntu). The shell is **bash**.
Windows PowerShell and `cmd.exe` are NOT available and MUST NOT be used.
These rules override every other instruction in this file.

### Hard rules for command execution

- Every command MUST be a POSIX/Linux command run through bash
  (e.g. `bash -lc "<command>"`).
- NEVER emit `powershell`, `powershell.exe`, `pwsh`, `-Command`,
  `New-Item`, `Add-Content`, `Set-Content`, `Get-ChildItem`,
  `Test-Path`, `$env:`, or any PowerShell syntax.
- NEVER emit Windows paths (`C:\...`, `\\?\...`). Use Linux paths
  under the WSL mount, e.g. `/mnt/c/Code/cs2-report` or, preferably,
  the WSL-native path `/home/<user>/code/cs2-report`.
- NEVER wrap a command in `powershell -Command "..."`.
- Do not use `cmd /c`, `start`, or `.bat`/`.ps1` files.
- Do not chain commands with `;` expecting PowerShell semantics.
  Use `&&`, `||`, pipes, and subshells as in bash.

### Preferred tools inside WSL

- File creation: `touch`, `cat > file <<'EOF' ... EOF`, `printf`.
- Text edits: `sed -i`, `perl -0pi -e`, `python3 - <<'PY' ... PY`,
  or `git apply` for patches.
- Inspection: `ls`, `cat`, `sed -n`, `grep -n`, `head`, `tail`,
  `git status`, `git diff`.
- Python: call `python3`, never `python` unless verified.
- Package installs: `apt`, `pip3`, `npm` inside WSL only.

### Python edit pattern (avoid quote-escaping hell)

When a change is too complex for `sed`, write a here-doc script
instead of an inline `-c` string:

    python3 - <<'PY'
    from pathlib import Path
    p = Path("app.py")
    s = p.read_text(encoding="utf-8")
    # ... targeted replace ...
    p.write_text(s, encoding="utf-8")
    PY

Do NOT generate `python -c "..."` one-liners containing quotes,
newlines, or f-strings — they break under shell escaping.

### Git workflow inside WSL

- Use LF line endings. Do not introduce CRLF.
- `git config core.autocrlf false` is expected in this repo.
- Verify edits with `git diff --check` and `git diff` before
  declaring completion.

### If a command fails

- Do not retry the same command.
- Do not switch to PowerShell as a workaround.
- Read the error, inspect the file, and choose a different
  bash-native approach (here-doc, `sed`, or `git apply`).

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

## Editing Strategy and Tool Selection

### 1. General Principles

- Prefer minimal, targeted modifications.
- Never rewrite an entire file when a smaller edit is sufficient.
- Read the latest version of a file before modifying it.
- Inspect relevant callers, dependencies, and tests before changing application logic.
- Preserve existing architecture, formatting, encoding, line endings, and unrelated user changes.
- Never assume a previous edit succeeded without reading the file back.

### 2. Editing Method Selection

Choose the editing method according to the scope of the change.

**Small, targeted changes**
- Use sed -i, perl -0pi -e, or a short python3 here-doc.
- Target the exact intended occurrence.
- Check that the expected match exists before modifying anything.
- Ensure the operation does not unintentionally modify multiple occurrences.

**Multi-line or structural changes**
- Prefer generating a unified diff patch.
- Validate it using git apply --check.
- Apply it using git apply.
- Inspect the resulting Git diff immediately.
- If patch application fails, inspect the current file and construct a corrected patch rather than repeating the same operation.

**New files**
- Use an appropriate file-creation method.
- Do not overwrite an existing file unintentionally.

**Full-file rewrites**
- Avoid them for ordinary changes.
- Only use them when the requested operation genuinely requires rebuilding the file.
- Preserve its original encoding, BOM status, line endings, and formatting.

### 3. Failed Edit Recovery

- Never repeat an identical failed editing operation.
- Read the current file again after an editing failure.
- Identify the actual reason for failure.
- Choose a different method or construct a corrected patch.
- Stop after two unsuccessful attempts and report the problem.
- Never claim that an edit succeeded based only on a command being executed.
- Never fall back to PowerShell or cmd.exe when a bash edit fails.

### 4. Verification Requirements

After every meaningful modification:

1. Read the modified file again.
2. Confirm the requested changes are present.
3. Confirm unrelated content remains unchanged.
4. Inspect git diff or an equivalent comparison for untracked files.
5. Run relevant syntax checks and tests.
6. Check git diff --check.
7. Report the actual files modified and tests executed.

### 5. Git and User-Change Protection

- Inspect git status --short before editing.
- Do not overwrite or discard existing uncommitted changes.
- Never use destructive Git commands to clean up unexpected changes.
- Do not stage or commit changes unless explicitly requested.
- Separate pre-existing modifications from changes made during the current task.

### 6. Completion Reporting

A task may only be reported as complete after:

- The requested implementation or documentation change is saved.
- Read-back verification succeeds.
- Relevant tests have actually run.
- Git changes have been inspected.
- Required project documentation and SESSION_HANDOFF.md have been updated.