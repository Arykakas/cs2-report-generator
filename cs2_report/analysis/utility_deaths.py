"""Deaths that happened while the player held utility."""

import polars as pl

from ..constants import UTILITY_WEAPONS


def analyze_utility_deaths(demo, target_player: str) -> dict:
    utility_deaths = demo.kills.filter(
        (pl.col("victim_name") == target_player)
        & pl.col("weapon").is_in(UTILITY_WEAPONS)
    )
    return {
        "utility_deaths": utility_deaths,
        "utility_death_ticks": utility_deaths.get_column("tick").to_list(),
    }
