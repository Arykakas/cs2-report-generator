"""Shared demo analysis orchestration for both report versions."""

import argparse
import os
from pathlib import Path
import sys

import polars as pl

from .analysis.aim import analyze_aim
from .analysis.archetype import analyze_archetype
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


def _archetype_inputs(hit_data: dict, aim: dict, flashes: dict, movement: dict, deaths, stats: dict) -> dict:
    rounds = int(number(stats.get("rounds_played", stats.get("rounds", 0))))
    successful_flashes = sum(row["enemies"] > 0 for row in flashes["flash_details"])
    success_rate = successful_flashes / flashes["flash_count"] if flashes["flash_count"] else 0.0
    return analyze_archetype(
        {"headshot_percentage": headshot_percentage(hit_data)},
        aim,
        {"flashbang_success_rate": success_rate},
        {
            "rifle_moving_percentage": movement["rifle_moving_percentage"],
            "utility_deaths": deaths.height,
            "rounds_played": rounds,
        },
    )


def main() -> None:
    args = parse_args()
    demo_path = args.demo.expanduser().resolve()
    _emit_progress(0.08, "Opening demo and reading match tables")
    demo = load_demo(demo_path)

    _emit_progress(0.22, "Finding the selected player")
    player_id, player_name, shots = resolve_player(demo, args.player.strip())

    _emit_progress(0.38, "Analyzing player performance")
    hits, movement, aim, utility_deaths, flashes = _analyze_player(
        demo, player_name, player_id, shots
    )
    stats_frame = demo.stats.filter(pl.col("name") == player_name)
    if stats_frame.is_empty():
        raise ValueError(f"No basic stats found for player name: {player_name}")
    player_stats = stats_frame.row(0, named=True)
    archetype = _archetype_inputs(
        hits["hit_model_data"], aim, flashes, movement, utility_deaths, player_stats
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
