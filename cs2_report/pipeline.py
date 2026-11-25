"""Shared demo analysis orchestration for both report versions."""

import argparse
import os
from pathlib import Path
import sys

import polars as pl

from .analysis.aim import analyze_aim
from .analysis.archetype import (
    calculate_player_scores,
    calculate_tie_aware_ranks,
    build_archetype_result,
)
from .analysis.flashes import analyze_flashes
from .analysis.hits import analyze_hits
from .analysis.utility_deaths import analyze_utility_deaths
from .analysis.weapons import analyze_weapon_movement
from .demo import load_demo, resolve_player
from .localization import DEFAULT_LOCALE, SUPPORTED_LOCALES, report_output_paths, translate
from .report_common import build_report_context, headshot_percentage, number
from .report_v1 import generate as generate_report_v1
from .report_v2 import generate as generate_report_v2

REPORT_GENERATORS = {
    "1.0": generate_report_v1,
    "2.0": generate_report_v2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a CS2 demo post-match report.")
    parser.add_argument("--demo", required=True, type=Path, help="Path to the .dem file")
    parser.add_argument("--player", required=True, help="Player name or SteamID64")
    parser.add_argument(
        "--report-version", choices=(*REPORT_GENERATORS, "all"), default="1.0",
        help="Report template version, or 'all' to generate both (default: 1.0)",
    )
    parser.add_argument(
        "--locale", choices=SUPPORTED_LOCALES, default=DEFAULT_LOCALE,
        help="Report language (default: en)",
    )
    return parser.parse_args()


def _emit_progress(fraction: float, message: str) -> None:
    if os.environ.get("CS2_REPORT_PROGRESS") == "1":
        print(f"CS2_PROGRESS|{fraction:.2f}|{message}", file=sys.stderr, flush=True)


def _analyze_player(demo, player_name: str, player_id: int, shots) -> tuple[dict, dict, dict, object, dict]:
    """Collect shared analysis results before selecting a report renderer."""
    hits = analyze_hits(demo, player_id)
    movement = analyze_weapon_movement(demo, shots, player_id)
    aim = analyze_aim(
        demo, shots, player_id,
        movement["angular_velocity_by_tick"],
        movement["angular_deviation_by_tick"],
        movement["shots_with_velocity"],
    )
    flashes = analyze_flashes(demo, player_id)
    utility_deaths = analyze_utility_deaths(demo, player_name)["utility_deaths"]
    return hits, movement, aim, utility_deaths, flashes


def build_match_context(demo, player_name, shots) -> tuple[list[dict], list[dict], list[dict]]:
    """Build normalized player records, teammates, and enemy context."""
    selected_stats = demo.stats.filter(pl.col("name") == player_name)
    if selected_stats.is_empty():
        return [], [], []

    selected_row = selected_stats.row(0, named=True)
    current_player_team = selected_row.get("team", "T")
    records = []
    teammates = []
    enemies = []

    for name in demo.stats["name"].unique().to_list():
        _, p_name, p_shots = resolve_player(demo, name)
        stats_frame = demo.stats.filter(pl.col("name") == name)
        if stats_frame.is_empty():
            continue

        row = stats_frame.row(0, named=True)
        team = row.get("team", "T")
        rounds_played = int(row.get("rounds_played", 0))
        is_active = rounds_played >= 3 and len(p_shots) >= 10

        opening_engagements = 0
        if "round" in p_shots.columns:
            round_shots = p_shots.sort("tick")
            for round_number in round_shots["round"].unique().to_list():
                in_round = round_shots.filter(pl.col("round") == round_number)
                if in_round.is_empty():
                    continue
                first_tick = in_round["tick"].min()
                first_shot = demo.shots.filter(pl.col("tick") == first_tick)
                if not first_shot.is_empty() and first_shot.get_column("name")[0] == p_name:
                    opening_engagements += 1
        elif not p_shots.is_empty():
            opening_engagements = 1

        record = {
            "name": p_name,
            "team": team,
            "rounds_played": rounds_played,
            "participation_score": rounds_played / max(1, int(row.get("total_rounds", 1))),
            "raw_stats": {
                "kd": float(row.get("kills", 0)) / max(1, float(row.get("deaths", 1))),
                "adr": float(row.get("adr", 0)),
                "headshot_pct": float(row.get("headshot_percentage", 0)),
            },
            "trait_components": {
                "aggression": {"raw": opening_engagements, "count": rounds_played},
                "precision": {"raw": 0, "count": 0},
                "utility": {"raw": 0, "count": 0},
                "positioning": {"raw": 0, "count": 0},
            },
        }

        if p_name == player_name:
            records.append(record)
        elif is_active and team == current_player_team:
            teammates.append(record)
        else:
            enemies.append(record)

    return records, teammates, enemies


def _score_relative_player(demo, record: dict, player_id: int = None, shots=None, hit_data: dict = None, movement: dict = None, flashes: dict = None, utility_deaths=None) -> dict:
    """Build a raw four-trait score for one eligible teammate comparison participant."""
    if hit_data is None:
        player_id, _, shots = resolve_player(demo, record["name"])
        hit_data = analyze_hits(demo, player_id)
        movement = analyze_weapon_movement(demo, shots, player_id)
        flashes = analyze_flashes(demo, player_id)
        utility_deaths = analyze_utility_deaths(demo, record["name"])["utility_deaths"]

    stats_frame = demo.stats.filter(pl.col("name") == record["name"])
    if stats_frame.is_empty():
        return {"name": record["name"], "scores": None, "available": False}

    stats = stats_frame.row(0, named=True)
    rounds_played = int(stats.get("rounds_played", 0))
    shot_count = len(shots) if shots is not None else int(hit_data.get("hit_count", 0))
    flash_count = int(flashes.get("flash_count", 0))
    utility_death_count = int(utility_deaths.height)

    hit_data = dict(hit_data)
    hit_data["count"] = shot_count

    positioning_data = {
        "opening_engagements": record["trait_components"]["aggression"]["raw"],
        "rounds_played": rounds_played,
        "utility_deaths": utility_death_count,
        "utility_damage": 0,
        "rifle_moving_percentage": movement.get("rifle_moving_percentage", 0),
    }
    raw_scores = calculate_player_scores(hit_data, {}, flashes, positioning_data)

    available = rounds_played >= 3 and shot_count >= 10
    return {
        "name": record["name"],
        "scores": raw_scores,
        "available": available,
        "sample_counts": {
            "rounds": rounds_played,
            "shots": shot_count,
            "flashes": flash_count,
        },
    }


def _archetype_inputs(hit_data: dict, aim: dict, flashes: dict, movement: dict, deaths, stats: dict, player_name: str = None, match_context: list[dict] = None, comparison_scores: list[dict] = None, locale: str = DEFAULT_LOCALE) -> dict:
    """Build raw and tie-aware relative trait scores for the selected player."""
    utility_death_rate = (
        max(0, int(deaths.height))
        / max(1, int(stats.get("rounds_played", 1)))
        * 100
    )
    positioning_data = {
        "opening_engagements": next((
            record["trait_components"]["aggression"]["raw"]
            for record in (match_context or [])
            if record["name"] == player_name
        ), 0),
        "rounds_played": int(stats.get("rounds_played", 1)),
        "utility_deaths": int(deaths.height),
        "utility_damage": 0,
        "rifle_moving_percentage": movement.get("rifle_moving_percentage", 0),
    }
    raw_scores = calculate_player_scores(hit_data, aim, flashes, positioning_data)

    traits = ("aggression", "precision", "utility", "positioning")
    eligible_comparisons = [
        item for item in (comparison_scores or [])
        if item.get("available") and item.get("scores")
    ]
    comparison_values = {
        trait: [item["scores"][trait] for item in eligible_comparisons]
        for trait in traits
    }
    ranked_scores = dict(raw_scores)

    selected_comparison = next((
        item for item in (comparison_scores or [])
        if item.get("name") == player_name
    ), None)
    selected_available = bool(selected_comparison and selected_comparison.get("available"))

    for trait in traits:
        if not selected_available:
            ranked_scores[trait] = 0.0
            ranked_scores[f"{trait}_rank"] = None
            ranked_scores[f"{trait}_is_max"] = False
            ranked_scores[f"{trait}_is_tied_leader"] = False
            continue
        ranking = calculate_tie_aware_ranks(comparison_values[trait], higher_is_better=True)
        relative_score = ranking["relative_scores"][raw_scores[trait]]
        ranked_scores[trait] = relative_score
        ranked_scores[f"{trait}_rank"] = ranking["ranks"][raw_scores[trait]]
        ranked_scores[f"{trait}_is_max"] = ranking["leader_flags"][raw_scores[trait]]
        ranked_scores[f"{trait}_is_tied_leader"] = raw_scores[trait] in ranking["tied_leaders"]

    ranked_scores["raw_scores"] = {
        trait: raw_scores[trait]
        for trait in traits
    }
    ranked_scores["comparison_players"] = [
        item["name"] for item in eligible_comparisons
    ]
    ranked_scores["availability"] = {
        "eligible": selected_available,
        "reason": "insufficient_samples" if not selected_available else "eligible",
    }
    ranked_scores["sample_counts"] = (
        selected_comparison.get("sample_counts", {})
        if selected_comparison
        else {}
    )

    archetype_result = build_archetype_result(ranked_scores, stats, locale)

    return {
        **archetype_result,
        "score_basis": {
            "headshot_percentage": hit_data.get("headshot_percentage"),
            "flashbang_success_rate": flashes.get("flashbang_success_rate"),
            "rifle_moving_percentage": movement.get("rifle_moving_percentage"),
            "utility_death_rate_per_round": utility_death_rate,
        },
    }

def main() -> None:
    args = parse_args()
    demo_path = args.demo.expanduser().resolve()
    locale = args.locale
    _emit_progress(0.08, translate(locale, "progress.open_demo"))
    demo = load_demo(demo_path)

    _emit_progress(0.22, translate(locale, "progress.find_player"))
    player_id, player_name, shots = resolve_player(demo, args.player.strip())

    # --- Build Context Records (Teammates/Enemies/Normalized Stats) ---
    records, teammates, enemies = build_match_context(demo, player_name, shots)

    _emit_progress(0.38, translate(locale, "progress.analyze_context"))
    hits = analyze_hits(demo, player_id)
    movement = analyze_weapon_movement(demo, shots, player_id)
    aim = analyze_aim(
        demo, shots, player_id,
        movement["angular_velocity_by_tick"],
        movement["angular_deviation_by_tick"],
        movement["shots_with_velocity"],
    )
    flashes = analyze_flashes(demo, player_id)
    utility_deaths = analyze_utility_deaths(demo, player_name)["utility_deaths"]

    # Update stats frame and check for presence
    stats_frame = demo.stats.filter(pl.col("name") == player_name)
    if stats_frame.is_empty():
        raise ValueError(f"No basic stats found for player name: {player_name}")
    player_stats = stats_frame.row(0, named=True)

    # Populate trait components in the context records
    hits["trait_components"]["precision"] = {"raw": hits.get("headshot_percentage", 0), "count": len(shots)}
    hits["trait_components"]["utility"] = {"raw": hits.get("utility_damage_sum", 0), "count": len(shots)}
    flashes["trait_components"]["utility"] = {"raw": flashes.get("flashbang_success_rate", 0), "count": 1}
    movement["trait_components"]["positioning"] = {"raw": movement.get("rifle_moving_percentage", 0), "count": len(shots)}

    # Score eligible teammates through the same canonical raw-score path.
    selected_record = next(record for record in records if record["name"] == player_name)
    comparison_scores = [
        _score_relative_player(
            demo,
            selected_record,
            player_id=player_id,
            shots=shots,
            hit_data=hits,
            movement=movement,
            flashes=flashes,
            utility_deaths=utility_deaths,
        )
    ]
    for teammate in teammates:
        comparison_scores.append(_score_relative_player(demo, teammate))

    # Generate archetype results using the new normalized scoring logic
    archetype_analysis = _archetype_inputs(
        hits, aim, flashes, movement, utility_deaths, player_stats,
        player_name=player_name,
        match_context=records + teammates,
        comparison_scores=comparison_scores,
        locale=locale,
    )

    _emit_progress(0.82, "Preparing report")
    context = build_report_context(
        demo_path=demo_path,
        demo=demo,
        player_name=str(player_name),
        player_stats=player_stats,
        target_shots=shots,
        hit_analysis=hits,
        movement=movement,
        aim=aim,
        flashes=flashes,
        utility_deaths=utility_deaths,
        archetype_analysis=archetype_analysis,
        locale=locale,
    )

    _emit_progress(0.82, translate(locale, "progress.prepare_report"))
    versions = REPORT_GENERATORS if args.report_version == "all" else (args.report_version,)
    outputs = []
    for version in versions:
        report_text, html_report = REPORT_GENERATORS[version](context)
        text_path, html_path = report_output_paths(demo_path, version, locale)
        text_path.write_text(report_text + "\n", encoding="utf-8")
        html_path.write_text(html_report, encoding="utf-8")
        outputs.append((report_text, text_path, html_path))

    _emit_progress(1.0, translate(locale, "progress.complete"))
    for report_text, text_path, html_path in outputs:
        print(report_text)
        print(f"\nReport saved to: {text_path}")
        print(f"HTML report saved to: {html_path}")

if __name__ == "__main__":
    main()
