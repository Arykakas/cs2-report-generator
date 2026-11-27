# Task 2 Context Definition Findings - Report 2.0 Module 1

## Current Implementation Status
The project already has a foundational implementation for player context in `pipeline.py` via the `build_match_context` function.

## Technical Details
- **Record Structure**: Each player is represented by a dictionary containing:
    - Identity: `name`, `team`.
    - Participation: `rounds_played`, `participation_score` (ratio of rounds played to total).
    - Raw Stats: `kd`, `adr`, `headshot_pct`.
    - Trait Components: Placeholders for `aggression`, `precision`, `utility`, and `positioning`.
- **Participation Threshold**: A check is already in place: players must have >=3 rounds played AND >=10 shots to be considered "active" for teammate comparisons.
- **Team Logic**: The system identifies the selected player's team and separates other players into `teammates` (same team) or `enemies` (different team).

## Decisions & Refinements
- **Side Awareness**: While teams are identified, explicit CT/T side-aware comparison logic needs to be finalized. We will prioritize side-aware comparisons when sample sizes allow, falling back to pooled match data otherwise.
- **Enemy Context**: Enemies are preserved in a separate list to ensure they provide context without polluting the teammate-relative ranking scores.
- **Data Separation**: Raw measurements remain distinct from relative ranks to allow the narrative engine to explain "why" a player received a specific score.

## Fallbacks
- Players failing the participation check are excluded from teammate rankings but remain in the report with an "Insufficient Data" status.
