# Report 2.0 Development Plan

For the project-wide sequence connecting Report 2.0, the in-app report
experience, and 2D replay, see [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).
This file tracks the report-specific scope. Module 1's detailed task list is
[REPORT_2_0_MODULE_1_TASKS.md](REPORT_2_0_MODULE_1_TASKS.md).

## Goal

Build a coaching-oriented report that describes a player's match-relative
playstyle, explains the impact of that playstyle, and gives clear next steps.
K/D and ADR remain visible, and poor performance should lead to direct
coaching without hiding the player's playstyle.

## Narrative flow

1. **Player archetype:** What playstyle did the player show relative to their
   teammates?
2. **Performance snapshot:** What happened, including K/D, ADR, and other
   contextualized stats?
3. **Coaching lab:** What symptom appeared, what likely caused it, and what can
   the player change?
4. **Training roadmap:** Which actionable drills address the identified
   weaknesses?

## Module 1: Match-relative archetype and narrative

The codebase contains an initial implementation of trait scoring and narrative
generation. Treat it as a prototype: the comparison rules, scoring inputs,
tie handling, stat normalization, and narrative path still need review and
consolidation.

- [ ] Complete the data audit and implementation tasks in
  `REPORT_2_0_MODULE_1_TASKS.md`.
- [ ] Compare archetypes against teammates; use enemy performance as additional
  context and account for side and rounds played where data supports it.
- [ ] Define aggression around fight initiation and time to engagement, then
  describe fight impact separately.
- [ ] Keep precision sample-aware and define utility only from flash, HE,
  molotov/incendiary, and validated smoke measures.
- [ ] Use tie-aware relative scores and preserve their raw metric basis.
- [ ] Normalize K/D, ADR, and other narrative inputs; make narratives
  deterministic and performance-aware.
- [ ] Consolidate scoring and archetype selection into one canonical path.

## Module 2: Performance snapshot

- [ ] Audit existing qualitative labels and ensure they match the displayed
  stats and their definitions.
- [ ] Add performance-aware feedback using normalized K/D, ADR, and agreed
  performance bands.
- [ ] Ensure low impact makes the feedback more direct without replacing the
  playstyle description with generic criticism.

## Module 3: Coaching lab

- [ ] Define the Skill Pillars: Aim & Mechanics, Movement & Positioning, and
  Tactical Awareness.
- [ ] Map supported data points into clear symptom → likely cause → fix cards.
- [ ] Identify the source metric for each card and avoid presenting uncertain
  explanations as proven causes.
- [ ] Where possible, connect a coaching card to a supporting round or moment
  in the in-app 2D replay, as planned in `PROJECT_ROADMAP.md`.

## Module 4: Training roadmap

- [ ] Generate fixed-template drills from weaknesses identified in Module 3.
- [ ] Tie each drill to a specific observed metric or behavior and give the
  player a clear practice goal.
- [ ] Avoid recommending drills when the underlying data has insufficient
  samples.

## Integration

- [x] Keep Report 2.0 generation separate from Report 1.0 while sharing the
  normalized analysis result where appropriate.
- [x] Render Report 2.0 as part of the app's primary in-app report view, with a
  standalone download as an optional action; see `PROJECT_ROADMAP.md`.
- [x] Ensure Report 2.0 and its download use the same metrics and narrative
  output.
- [x] Preserve Report 1.0 behavior and output format.
