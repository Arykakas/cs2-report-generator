# Report 2.0 Development Plan

## Goal
Transition from a data-heavy summary to a coaching-oriented diagnostic tool that explains *why* metrics matter.

## Narrative Flow
1. **Player Archetype**: Who are you? (e.g., "The High-Octane Rusher")
2. **Performance Snapshot**: What happened? (Contextualized stats)
3. **Coaching Lab**: Why did it happen? (Symptom -> Cause -> Fix)
4. **Training Roadmap**: How do I fix it? (Actionable drills)

## Module 1: Player Archetype & Dynamic Summary
- [x] Define Trait Scores (Aggression, Precision, Utility, Positioning)
- [x] Implement scoring logic in `cs2_report/analysis/archetype.py`
- [x] Create the fixed-template narrative engine for dynamic summaries
- [x] Integrate into the Report 2.0 rendering pipeline

Positioning currently scores rifle movement discipline and utility deaths per round. Utility scores the share of thrown flashes that blinded at least one enemy. These are match-level indicators, not positional heatmap measurements.

## Module 2: Performance Snapshot
- [ ] Contextualize existing stats (Accuracy, ADR, etc.) with qualitative labels
- [ ] Add "Performance-Aware" feedback to archetypes: Ensure narrative summaries reflect whether a player is meeting expectations for their role (e.g., a Rusher with low K/D should receive corrective coaching rather than just praise).

## Module 3: The Coaching Lab
- [ ] Define Skill Pillars:
    - Aim & Mechanics
    - Movement & Positioning
    - Tactical Awareness
- [ ] Map data points to "Symptom -> Cause -> Fix" cards

## Module 4: Training Roadmap
- [ ] Generate actionable drills based on identified weaknesses in Module 3
