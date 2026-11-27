# Report 2.0 Module 1: Match-Relative Archetypes and Narrative

## Purpose

Build a coaching summary that describes how a player played relative to their
teammates, uses the opposing team as additional match context, and explains
whether that playstyle produced impact. Keep the player's basic K/D and ADR
visible regardless of archetype. A poor result should make the coaching more
direct without hiding or relabeling the player's playstyle.

This file is a work plan only. The tasks below do not imply that implementation
has started.

## Agreed product decisions

- Compare the selected player with **their teammates** when assigning relative
  trait ranks and archetypes.
- Use the enemy team as additional context when the available data supports a
  useful comparison.
- Account for team, side, and rounds played where the demo data allows. Do not
  build map-specific timing expectations or map-position scripts.
- Aggression is about **initiating fights and how quickly the player gets into
  those fights**. Describe it separately from whether those fights were
  successful. An aggressive player may have a short life or high-impact
  highlights; use measurable opening-fight and outcome data to explain which.
- Precision should describe demonstrated accuracy/aim quality, with sample
  size considered.
- Utility should measure utility use only: flashes, HE grenades,
  molotovs/incendiaries, and smokes. Do not include utility deaths or rifle
  movement in the utility trait.
- For flashes, account for how many enemies were blinded and for how long, if
  the library exposes reliable duration data. For HE and molotov/incendiary,
  use utility damage. Investigate smoke data before deciding how to score
  tactical smoke performance; do not invent a smoke-success metric if the data
  cannot support it.
- Ties are valid results. Every player tied for a rank or distinction must
  receive equal recognition; do not select one arbitrarily.
- Narratives should state the playstyle explicitly, then explain its impact.
  Low K/D and ADR should lead to more candid coaching, not erase the playstyle
  description. K/D and ADR remain visible in the report.
- Narrative output must be deterministic: the same inputs should produce the
  same text.
- Use one canonical scoring and archetype-selection path. Normalize stat names
  before scoring and narrative generation.

## Task 1: Audit available demo data

- [x] Inspect the installed `awpy` version and actual schemas used by this
  project for kills, damages, shots, rounds, grenades, blinds, and player/team
  state.
- [x] Identify reliable fields for attacker/victim team and side, round,
  player participation, opening engagements, and time from round start to
  first engagement.
- [x] Identify whether flash blindness duration is available per victim and
  can be associated reliably with the flash thrower.
- [x] Identify HE and molotov/incendiary damage attribution and how to avoid
  double-counting damage events.
- [x] Inspect smoke-related events or state. Document what can be measured
  (for example, duration, location, visibility/obscuration, or enemy
  interaction) and what cannot.
- [x] Record data gaps and fallback behavior in this file before choosing
  scoring formulas.

**Done when:** each candidate metric has a verified source field/table, its
unit, its attribution rules, and a documented fallback for missing data.

See also: [analysis_audit_findings.md](analysis_audit_findings.md)

## Task 2: Define the player and comparison context

- [x] Create one normalized per-player match record containing player identity,
  team, side participation, rounds played, kills, deaths, ADR, and the raw
  components required by the traits.
- [x] Decide how to combine a player's CT and T halves. Prefer side-aware
  comparisons when samples are sufficient; define a documented fallback to
  pooled match data when they are not.
- [x] Use teammate comparisons for archetype ranks. Preserve enemy metrics as
  contextual reference data rather than mixing both teams into teammate ranks.
- [x] Exclude or specially handle players with too little participation to
  support a meaningful comparison.
- [x] Keep raw measurements separate from relative ranks so the report can
  explain why a player received a score.

**Done when:** every player in the demo has a consistent context record and
comparison group, with team, side, and sample coverage represented explicitly.

See also: [context_definition_findings.md](context_definition_findings.md)

## Task 3: Define trait inputs and scoring rules

- [x] **Aggression:** choose verified measures of fight initiation and time to
  engagement. Prefer opening/first engagements and per-round rates over raw
  kill or shot counts. Keep fight initiation separate from duel success.
- [x] **Aggression impact:** define supporting outcomes such as opening duel
  wins/losses, first deaths, opening kills, and their relationship to K/D and
  ADR. Use these to qualify the narrative, not to redefine aggression itself.
- [x] **Precision:** define a documented combination of suitable aim/accuracy
  measures. Decide how to handle players with few shots or kills so a tiny
  sample does not dominate the ranking.
- [x] **Utility:** define per-type components for enemy flash count and blind
  duration, HE and molotov/incendiary damage, and any smoke measure validated
  by Task 1. Include teammate/self harm as a penalty if attribution is
  reliable.
- [x] Normalize for opportunity where appropriate (per round, per throw, or
  per engagement), and avoid rewarding volume alone.
- [x] Keep positioning separate from utility. Document its inputs and ensure
  any utility-death measure is categorized consistently.
- [x] Define missing-data and low-sample behavior for every trait. Missing data
  must not silently become a meaningful zero score.

**Done when:** each trait has a written formula, metric units, sample rules,
missing-data behavior, and at least one worked example.

## Task 4: Implement tie-aware relative scoring

**Status:** Completed. The shared dense-rank helper, eligible teammate raw-score loop, tie/leader metadata, and focused unit cases are implemented and verified.

- [x] Replace the current first-match rank calculation with tie-aware ranking.
- [x] Ensure tied players receive identical ranks and all tied leaders are
  identified as leaders.
- [x] Define how relative scores behave when all eligible teammates have the
  same value and when only one player has enough data.
- [x] Keep raw scores, relative ranks, tie/leader flags, sample counts, and
  confidence/availability metadata in separate fields.
- [x] Verify rank bounds and ordering for low-to-high and high-to-low traits.

**Done when:** tied values never receive different ranks due to player order,
and score behavior is defined for all-equal and single-player comparisons.

## Task 5: Define archetypes from playstyle combinations

**Status:** Completed. Archetype labels are selected from relative trait combinations, tied traits are preserved as distinctions, and insufficient-data is explicit.

- [x] Specify archetypes as combinations of relative traits (for example,
  aggressive/precise, aggressive/low-impact, passive/precise, or passive/low
  impact), rather than a single highest trait.
- [x] Decide how ties across trait ranks affect archetype labels. Preserve
  multiple distinctions when the data supports a tie instead of forcing a
  unique winner.
- [x] Use teammate ranks for the label and enemy context to explain how the
  player's team style compared with the opposition, when useful and supported.
- [x] Avoid assigning a confident archetype when the required metrics have
  insufficient samples; use a clear low-confidence or insufficient-data
  result.

**Done when:** archetype selection is deterministic, tie-aware, sample-aware,
and has documented examples for every supported combination.

## Task 6: Build performance-aware, deterministic narratives

**Status:** Completed. Narratives use normalized K/D and ADR, fixed performance bands, explicit playstyle statements, and deterministic fixed-template wording.

- [x] Define a canonical normalized stats object, including derived K/D and
  ADR, and pass that same structure to scoring and narrative generation.
- [x] Verify every narrative threshold reads a real normalized key; remove
  silent default-to-zero behavior for required metrics.
- [x] Keep the playstyle statement explicit in every narrative, including when
  K/D or ADR is poor.
- [x] Add outcome wording that distinguishes effective aggression from
  aggressive, low-impact play, and precise play from precision without enough
  round impact.
- [x] Set explicit performance bands or comparison rules for K/D and ADR.
  Low performance should trigger direct corrective language without blindly
  praising the player.
- [x] Use fixed templates and deterministic selection. Avoid random phrase
  selection.
- [x] Keep language concise and understandable to an average CS2 player; show
  the relevant metric that supports each conclusion.

**Done when:** identical input data always yields identical narrative text,
and test cases cover high/low trait ranks crossed with high/low K/D and ADR.

## Task 7: Consolidate implementation and integrate Report 2.0

**Status:** Completed. The pipeline routes through `build_archetype_result()`, the unused `archetype_tmp.py` path is removed, and both report versions generate from the shared context.

- [x] Select one canonical scoring/archetype API and remove or adapt the
  competing unused scoring path.
- [x] Keep demo extraction, scoring, narrative decisions, and HTML rendering
  in their appropriate modules.
- [x] Pass raw metrics, relative ranks, tie flags, and narrative fields through
  the Report 2.0 context explicitly.
- [x] Update the trait cards and archetype summary so displayed labels explain
  that scores are relative to teammates in this match.
- [x] Preserve Report 1.0 behavior and output formats.

**Done when:** Report 2.0 uses the canonical result end to end, while Report
1.0 output remains unchanged.

## Task 8: Verify with focused cases and real demos

**Status:** Completed for the available `test.dem` scope. Ranking, side-fallback, narrative, canonical, both-version, utility, and repeated-run checks pass. Cross-demo verification remains naturally limited because only one `.dem` file is available.

- [x] Add unit-level coverage for formulas, missing data, low samples, side
  splits, ties, all-equal values, and leader recognition.
- [x] Add narrative cases for the same playstyle with strong versus poor K/D
  and ADR, confirming the tone changes but the playstyle remains explicit.
- [x] Verify available flash duration, grenade, and smoke event examples against
  event examples from real demos.
- [x] Generate Report 2.0 for the available demo and confirm ranks are teammate
  relative, enemy context is clearly labeled, and repeated runs are
  deterministic.
- [x] Confirm Report 1.0 still generates with its existing format.

**Done when:** focused cases pass and rendered reports show defensible,
traceable scores and narratives across varied matches.

## Deferred decisions to resolve during discovery

- Exact aggression fields depend on the verified `awpy` event schema. The goal
  is fight initiation and time-to-engagement, without map-specific timing
  scripts.
- The smoke scoring component must remain unspecified until Task 1 establishes
  what the library can measure reliably.
- Exact performance bands for K/D and ADR should be chosen after inspecting
  real match distributions and deciding whether to use absolute thresholds,
  teammate-relative thresholds, or both.
