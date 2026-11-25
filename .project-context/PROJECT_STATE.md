# Project State: CS2 Match Analyzer

## Overview
- **Project Name**: CS2 Report
- **Purpose**: A local Counter-Strike 2 demo analysis application that generates detailed player performance reports and interactive visualizations.
- **Technology Stack**: Python, Streamlit, Awpy (demo parsing), HTML/JS (visualizations).

## Architecture
- **Entry Point**: `app.py` (Streamlit UI)
- **Analysis Pipeline**: `pipeline.py` (Data extraction and processing)
- **Report Generation**: `report.py` (Narrative generation and rendering)
- **Integration Layer**: `analysis_wrapper.py`

## Development Milestones
- **Current Milestone**: Report 2.0 - Primary in-app report experience; Module 1 is complete for the available demo scope.
- **Verified Completed Tasks**:
    - [x] Task 1: Audit available demo data (analysis_audit_findings.md)
    - [x] Task 2: Define the player and comparison context (context_definition_findings.md)
    - [x] Task 3: Define trait inputs and scoring rules (documented; implementation remains prototype-only)
- **Current In-Progress Work**:
    - [x] Task 7: Consolidate implementation and integrate Report 2.0 (including inline app view and download action)
    - [x] Task 8: Verify with focused cases and the available real demo (completed within single-demo scope)
- **Remaining Major Workstreams**:
    - Module 2: Performance snapshot & Qualitative Feedback
    - Module 3: Coaching lab (Skill Pillars)
    - Module 4: Training roadmap
    - Localization: English, Danish, and Russian confirmed; Task 1 terminology policy complete

## Design Decisions & Implementation Status
- **Side-Aware Comparison**: Decision to prefer side-aware comparisons for CT/T halves when sample sizes are sufficient is complete. Pooled match data is the documented fallback for insufficient samples. Implementation verification of this logic is pending.

## Important Source Files
- `app.py`: Main UI logic and Streamlit configuration.
- `pipeline.py`: Core data processing and player context building.
- `report.py`: Narrative generation engine.
- `app.py`: In-app report review, version selection, and download action.
- `cs2_report/analysis/hits.py`: Bullet heatmap and hit analysis logic.

## Documentation References
- [REPORT_2_0_PLAN.md](/C:/Code/cs2-report/REPORT_2_0_PLAN.md)
- [REPORT_2_0_MODULE_1_TASKS.md](/C:/Code/cs2-report/REPORT_2_0_MODULE_1_TASKS.md)
- [analysis_audit_findings.md](/C:/Code/cs2-report/analysis_audit_findings.md)
- [context_definition_findings.md](/C:/Code/cs2-report/context_definition_findings.md)
