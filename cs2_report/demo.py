"""Demo loading and player identity resolution."""

from pathlib import Path

import polars as pl
from awpy import Demo


def load_demo(demo_path: Path) -> Demo:
    """Load tables used across the report pipeline."""
    demo = Demo(demo_path)
    demo.load("shots", "kills", "grenades", "blinds")
    return demo


def resolve_player(demo: Demo, player_input: str) -> tuple[int, str, pl.DataFrame]:
    """Resolve a name first, then a numeric SteamID64, to shot rows."""
    player_input = player_input.strip()
    target_shots = demo.shots.filter(pl.col("name") == player_input)

    if target_shots.is_empty():
        try:
            player_steamid = int(player_input)
        except ValueError as exc:
            raise ValueError(
                f"No shots found for player name or Steam ID: {player_input}"
            ) from exc
        target_shots = demo.shots.filter(pl.col("steamid") == player_steamid)

    if target_shots.is_empty():
        raise ValueError(f"No shots found for player name or Steam ID: {player_input}")

    player_steamid = target_shots.get_column("steamid")[0]
    target_player = str(target_shots.get_column("name")[0])
    return player_steamid, target_player, target_shots
