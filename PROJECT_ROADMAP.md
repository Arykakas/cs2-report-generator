# CS2 Match Analyzer: Product Roadmap

## Product goal

Turn a CS2 demo into an in-app match review that explains the player's
performance, lets them inspect relevant moments in a 2D replay, and offers a
downloadable report when they want to keep or share it.

## Intended user flow

1. Upload a `.dem` file and select a player.
2. Analyze the demo and show progress in the app.
3. Open the completed report directly in the app, keeping the app's navigation
   and visual style consistent.
4. Let the user move from a report finding into a relevant round or moment in
   the 2D replay when replay data is available.
5. Offer a standalone report download as a secondary action.

The app view is the primary experience. The download is generated from the same
analysis result so the two views do not develop separate scoring logic.

## Workstreams and sequence

### 0. Stabilize analysis data contracts

- [ ] Inspect the active app, report, and pipeline implementations before
  changing them; confirm their current responsibilities and callers.
- [ ] Define a shared analysis result structure that can feed the in-app view,
  Report 1.0, Report 2.0, and later replay links.
- [ ] Keep expensive demo parsing separate from rendering and avoid reparsing
  the demo for ordinary UI interactions.

**Exit condition:** one analysis run produces reusable results that renderers
can consume without rerunning demo parsing.

### 1. Report 2.0: player context and coaching

Follow [REPORT_2_0_PLAN.md](REPORT_2_0_PLAN.md) for the broader report work and
[REPORT_2_0_MODULE_1_TASKS.md](REPORT_2_0_MODULE_1_TASKS.md) for the detailed
match-relative archetype and narrative tasks.

- [ ] Audit available `awpy` data and validate the metrics before choosing
  formulas for aggression, precision, and utility.
- [ ] Compare archetype ranks against teammates, accounting for side and rounds
  played where data permits; use enemies as additional context.
- [ ] Add tie-aware relative scores, sample-aware confidence, and deterministic
  narratives that describe both playstyle and impact.
- [ ] Ensure K/D and ADR contribute to narrative tone using normalized,
  verified stat fields.
- [ ] Define the remaining performance snapshot, coaching lab, and training
  roadmap modules in `REPORT_2_0_PLAN.md`.

**Exit condition:** Report 2.0 has traceable metrics, understandable
match-relative scores, and repeatable narratives; Report 1.0 remains supported.

### 2. In-app report as the primary result

- [ ] Review the current Streamlit upload, player selection, progress,
  preview, and download flow before replacing or rearranging it.
- [ ] After analysis, show the report within the app rather than requiring the
  user to open a separate HTML file.
- [ ] Keep the report view consistent with the app's styling and navigation.
- [ ] Keep report state available across Streamlit reruns so interactions do
  not return the user to the upload screen or repeat analysis.
- [ ] Make download a secondary action and let the user select Report 1.0 or
  Report 2.0 where both are available.
- [ ] Generate the in-app view and downloadable output from the same analysis
  data and metric definitions.

**Exit condition:** the normal path is analyze → view report in the app →
optionally download, with stable state and no redundant demo parsing.

### 3. 2D replay: data and coordinate proof of concept

- [ ] Inspect `awpy` snapshots/events for player positions, rounds, kills,
  deaths, grenades, and side/team state; record sampling cost and missing data.
- [ ] Choose one supported map and verify the mapping from game world
  coordinates to its radar image (scale, offset, and orientation).
- [ ] Extract a compact position/event timeline for one round and render player
  positions at selected times.
- [ ] Validate paths and event timing against the in-game demo before building
  playback controls.
- [ ] Check map asset sources and licensing before bundling radar images.

**Exit condition:** one round on one map can be replayed with positions and
events accurately aligned to the radar at an acceptable parse and memory cost.

### 4. 2D replay: interactive review

- [ ] Add round selection, play/pause, timeline scrubbing, and playback speed.
- [ ] Add player filtering, paths, deaths/kills, and grenade markers based on
  validated data.
- [ ] Keep replay interactions in the browser/UI layer and operate on extracted
  replay data instead of rerunning the full demo parser.
- [ ] Add round/event anchors so relevant report findings can open the replay
  at the supporting moment.
- [ ] Define graceful behavior for unsupported maps or incomplete replay data.

**Exit condition:** users can inspect a supported round smoothly and navigate
from a report insight to its relevant replay moment.

### 5. Quality, performance, and release readiness

- [ ] Measure parsing time and memory use on small and large demos.
- [ ] Verify team/side changes, round boundaries, player death/spawn state,
  missing events, and low-sample player data.
- [ ] Verify report downloads and both report versions against existing output
  expectations.
- [ ] Confirm UI reruns, report interactions, and replay scrubbing do not
  unexpectedly repeat analysis.
- [ ] Document supported maps, known data limits, and how to add/calibrate map
  assets.

**Exit condition:** core flows work on representative demos with limitations
clearly handled and no regressions to existing report generation.

## Dependencies and design constraints

- Validate library data before treating a derived value as a coaching fact.
- Preserve raw measurements alongside relative scores so users can understand
  why a ranking was assigned.
- Relative trait comparisons are within the selected player's team; enemy
  performance is contextual unless a task explicitly defines another use.
- Side and rounds played should be accounted for where reliable, with explicit
  low-sample behavior.
- Utility must describe flash, HE, molotov/incendiary, and smoke use only.
  Smoke scoring remains undecided until the available data is verified.
- Keep analysis, UI state, report rendering, and replay visualization separated
  enough that report/replay interactions do not trigger parsing again.
- Do not embed a full interactive replay into the downloadable report as an
  initial requirement; prioritize the in-app replay and keep downloads focused.

## Current status

This roadmap records intended work, not completion. The existing Report 2.0
implementation is a starting point; its current scoring and narrative logic
needs the audit and redesign described in the linked Module 1 task file. The
current Streamlit experience and replay data costs must be inspected before
implementation estimates or supported-map commitments are made.
