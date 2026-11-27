# Task 3 Subtasks - Trait Scoring Refinement

This file tracks the remaining requirements for Task 3: "Define trait inputs and scoring rules".

## Progress Overview
- [ ] Subtask 3.1: Integrate Aggression Impact Outcomes
- [ ] Subtask 3.2: Implement advanced Utility metrics (Flash duration, teammate/self harm penalties)
- [ ] Subtask 3.3: Implement Sample Rule enforcement and "Low Confidence" flagging
- [ ] Subtask 3.4: Finalize Data Pipeline integration for `opening_engagements`

---

## Subtask Details

### Subtask 3.1: Integrate Aggression Impact Outcomes
**Goal**: Define and integrate supporting outcomes to qualify the narrative (e.g., opening duel wins/losses, first deaths).
- [ ] Identify specific fields in `demo.kills` and `demo.shots` for "opening" status.
- [ ] Update `calculate_player_scores` to include these as raw components.
- [ ] Update `generate_narrative` to use these outcomes to qualify the aggression description (e.g., "High impact" vs "Low impact").

### Subtask 3.2: Implement advanced Utility metrics
**Goal**: Incorporate flash duration and teammate/self harm penalties into utility scoring.
- [ ] Extract blind duration from `demo.blinds` (if available) or use the current proximity window as a proxy.
- [ ] Calculate "teammate/self harm" penalty by checking if `victim_steamid` in `demo.blinds` matches player's team or self.
- [ ] Update utility formula to subtract these penalties from the base score.

### Subtask 3.3: Implement Sample Rule enforcement and "Low Confidence" flagging
**Goal**: Ensure scores are only presented as high-confidence when sample sizes meet requirements.
- [ ] Add a `confidence_score` or `is_low_confidence` flag to the return dict of `calculate_player_scores`.
- [ ] Implement logic for:
    - Aggression: < 5 rounds
    - Precision: < 20 shots
    - Utility: < 2 throws
    - Positioning: < 3 rounds
- [ ] Update narrative engine to use "Low Confidence" flags to adjust the tone of the coaching.

### Subtask 3.4: Finalize Data Pipeline integration for `opening_engagements`
**Goal**: Ensure the pipeline correctly calculates and passes opening engagement data.
- [ ] Modify `build_match_context` in `pipeline.py` to calculate `opening_engagements`.
- [ ] Verify that this value is correctly passed into the `archetype_analysis` call.
