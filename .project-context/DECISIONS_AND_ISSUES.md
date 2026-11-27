# Decisions and Issues

## Architectural & Product Decisions
- **Teammate Comparison**: Archetypes and trait ranks are relative to teammates, not the whole match.
- **Enemy Context**: Enemy team data is used for contextual reference only, never mixed into teammate ranking scores.
- **Aggression Definition**: Defined as fight initiation and time-to-engagement; separated from duel success/outcome.
- **Utility Scope**: Limited to flashes, HE grenades, molotovs/incendiaries, and validated smoke measures.
- **Narrative Determinism**: All narrative outputs must be deterministic based on normalized stats.
- **Report 1.0 Preservation**: Existing report formats and behavior must remain unchanged.

## Technical Decisions & Rationale
- **Flash Duration Workaround**: Using a <=2 tick proximity window because `awpy` does not provide explicit duration data.
- **Player Participation Threshold**: Players must have >=3 rounds and >=10 shots to be included in teammate rankings (prevents outliers from small samples).
- **Data Separation**: Raw measurements are kept distinct from relative ranks to allow the narrative engine to explain "why" a score was given.

## Known Bugs & Unresolved Problems
- [ ] **Smoke Success Metric**: No reliable smoke-obscuration metric currently exists in `awpy`. Decision: focus on flash/utility damage for now.
- [x] **Side Awareness Verification**: Pooled match data and the side-aware-to-pooled fallback are implemented and unit-covered. Full side-aware pipeline splitting remains a future implementation decision outside the current single-demo verification scope.
- [x] **Teammate Trait Scoring**: Eligible teammates are scored through the canonical raw-score path and passed to `calculate_tie_aware_ranks()` with selected-player metadata.
- [x] **Narrative Test Coverage**: K/D and ADR bands, missing stats, low/high performance, and deterministic text are unit-tested.

## Failed Approaches
- **Map-Specific Timing Scripts**: Rejected during discovery as they were deemed too complex and not supported by current demo data schemas.
- **Broad Exception Handling**: Avoided in `pipeline.py` to ensure clear error reporting for corrupted demo files.
