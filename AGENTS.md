
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

## Before modifying the project
- Read relevant existing implementations.
- Check callers and dependencies.
- Identify the canonical file to modify.
- Never assume a backup or experimental file
  is the active implementation.
