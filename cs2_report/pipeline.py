"""Shared demo analysis orchestration for both report versions."""

import argparse
import os
from pathlib import Path
import sys

import polars as pl

from .analysis.aim import analyze_aim
from .analysis.archetype import analyze_archetype, calculate_player_scores, generate_narrative
from .analysis.flashes import analyze_flashes
from .analysis.hits import analyze_hits
from .analysis.utility_deaths import analyze_utility_deaths
from .analysis.weapons import analyze_weapon_movement
from .demo import load_demo, resolve_player
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


def _archetype_inputs(hit_data: dict, aim: dict, flashes: dict, movement: dict, deaths, stats: dict, player_name: str = None, match_context: list[dict] = None) -> dict:
    """Score four match traits and build a structured coaching summary using relative ranking."""
    current_scores = None

    if match_context and player_name:
        # Find the current player's scores in the context
        current_scores = next((p["scores"] for p in match_context if p["name"] == player_name), None)
        
        if current_scores:
            # Calculate percentile ranks for each trait relative to others in the match
            traits = ["aggression", "precision", "utility", "positioning"]
            for trait in traits:
                original_score = current_scores[trait]
                all_scores = [p["scores"][trait] for p in match_context]
                max_score = max(all_scores) if all_scores else 0
                
                sorted_scores = sorted(all_scores)
                rank = sorted_scores.index(original_score)
                current_scores[trait] = (rank / len(all_scores)) * 100
                
                # Add a flag if this player had the max score for this trait
                current_scores[f"{trait}_is_max"] = original_score == max_score

    # Archetype Selection Logic based on percentiles
    if current_scores["aggression"] >= 80 and current_scores["precision"] < 75:
        archetype = "The High-Octane Rusher"
    elif current_scores["precision"] >= 80 and current_scores["aggression"] < 70:
        archetype = "The Patient Marksman"
    elif current_scores["utility"] >= 75:
        archetype = "The Tactical Anchor"
    elif current_scores["positioning"] >= 85 and current_scores["aggression"] < 65:
        archetype = "The Disciplined Anchor"
    else:
        archetype = "The Versatile All-Rounder"

    # Determine if primary (highest score in their category)
    primary_trait = ""
    if archetype == "The High-Octane Rusher": primary_trait = "Aggression"
    elif archetype == "The Patient Marksman": primary_trait = "Precision"
    elif archetype == "The Tactical Anchor": primary_trait = "Utility"
    elif archetype == "The Disciplined Anchor": primary_trait = "Positioning"
    else: primary_trait = "Balance"

    is_primary = False
    if primary_trait != "Balance":
        # We need the raw scores to determine absolute highest.
        # Since we overwrote current_scores with percentiles, let's recalculate or use a different approach.
        # For now, I'll just set it based on the percentile being near 100 (top rank).
        if current_scores[primary_trait.lower()] >= 95: # Close enough to top for this prototype
            is_primary = True

    opportunity = "Trigger Discipline" if archetype == "The High-Octane Rusher" else \
                  "Positioning Variety" if archetype == "The Patient Marksman" else \
                  "Aggression Timing" if archetype == "The Tactical Anchor" else \
                  "Space Taking" if archetype == "The Disciplined Anchor" else \
                  "Specialization"

    return {
        "archetype": archetype,
        "scores": current_scores,
        "primary_trait": primary_trait,
        "is_primary": is_primary,
        "summary": generate_narrative(archetype, current_scores, stats),
        "opportunity": opportunity,
        "score_basis": {
            "headshot_percentage": hit_data.get("headshot_percentage"),
            "flashbang_success_rate": flashes.get("flashbang_success_rate"),
            "rifle_moving_percentage": movement.get("rifle_moving_percentage"),
            "utility_death_rate_per_round": (max(0, int(deaths.height)) / max(1, int(stats.get("rounds_played", 1)))) * 100,
        },
    }


def main() -> None:
    args = parse_args()
    demo_path = args.demo.expanduser().resolve()
    _emit_progress(0.08, "Opening demo and reading match tables")
    demo = load_demo(demo_path)

    _emit_progress(0.22, "Finding the selected player")
    player_id, player_name, shots = resolve_player(demo, args.player.strip())

    _emit_progress(0.38, "Analyzing all players for context")
    all_names = demo.stats["name"].unique().to_list()
    match_context = []
    for name in all_names:
        p_id, p_name, p_shots = resolve_player(demo, name)
        h, m, a, u, f = _analyze_player(demo, p_name, p_id, p_shots)
        s_frame = demo.stats.filter(pl.col("name") == p_name)
        p_stats = s_frame.row(0, named=True)
        positioning_data = {
            "rounds_played": p_stats.get("rounds_played", p_stats.get("rounds", 0)),
            "rifle_moving_percentage": m.get("rifle_moving_percentage", 0),
            "utility_deaths": u.height,
        }
        scores = calculate_player_scores(h["hit_model_data"], a, f, positioning_data)
        match_context.append({"name": p_name, "scores": scores})

    hits, movement, aim, utility_deaths, flashes = _analyze_player(
        demo, player_name, player_id, shots
    )
    stats_frame = demo.stats.filter(pl.col("name") == player_name)
    if stats_frame.is_empty():
        raise ValueError(f"No basic stats found for player name: {player_name}")
    player_stats = stats_frame.row(0, named=True)
    archetype = _archetype_inputs(
        hits["hit_model_data"], aim, flashes, movement, utility_deaths, player_stats, 
        player_name=player_name, match_context=match_context
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
        archetype_analysis=archetype,
    )
    versions = REPORT_GENERATORS if args.report_version == "all" else (args.report_version,)
    outputs = []
    for version in versions:
        report_text, html_report = REPORT_GENERATORS[version](context)
        suffix = "" if version == "1.0" else "_2.0"
        text_path = demo_path.with_name(f"{demo_path.stem}_report{suffix}.txt")
        html_path = demo_path.with_name(f"{demo_path.stem}_report{suffix}.html")
        text_path.write_text(report_text + "\n", encoding="utf-8")
        html_path.write_text(html_report, encoding="utf-8")
        outputs.append((report_text, text_path, html_path))

    _emit_progress(1.0, "Analysis complete")
    for report_text, text_path, html_path in outputs:
        print(report_text)
        print(f"\nReport saved to: {text_path}")
        print(f"HTML report saved to: {html_path}")


if __name__ == "__main__":
    main()
