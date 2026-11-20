"""Movement, velocity, and weapon-category shot metrics."""

import math

import polars as pl

from ..constants import (
    ANGULAR_LOOKBACK_TICKS,
    DEAGLE_USP,
    MOVEMENT_VELOCITY_THRESHOLD,
    PISTOL_WEAPONS,
    RIFLE_WEAPONS,
    SMG_WEAPONS,
    SNIPER_WEAPONS,
)


def calculate_weapon_metrics(shots_with_velocity: pl.DataFrame, weapons: list[str]):
    category_shots = shots_with_velocity.filter(pl.col("weapon").is_in(weapons))
    moving = category_shots.filter(pl.col("velocity") > MOVEMENT_VELOCITY_THRESHOLD)
    total = category_shots.height
    percentage = moving.height / total * 100 if total else 0.0
    return total, moving.height, percentage, moving


def analyze_weapon_movement(demo, target_shots: pl.DataFrame, player_steamid: int) -> dict:
    """Request snapshots once and derive shot speed and movement summaries."""
    all_shot_ticks = target_shots.get_column("tick").to_list()
    snapshot_ticks = sorted(
        set(all_shot_ticks)
        | {
            tick - ANGULAR_LOOKBACK_TICKS
            for tick in all_shot_ticks
            if tick >= ANGULAR_LOOKBACK_TICKS
        }
    )
    snapshots = demo.snapshots(ticks=snapshot_ticks)
    pre_shot_states = {
        row["tick"]: row
        for row in snapshots.filter(pl.col("steamid") == player_steamid)
        .select("tick", "pitch", "yaw")
        .to_dicts()
    }
    tick_rate = demo.tick_rate
    angular_velocity_by_tick = {}
    angular_deviation_by_tick = {}
    for shot in target_shots.to_dicts():
        before_tick = shot["tick"] - ANGULAR_LOOKBACK_TICKS
        before = pre_shot_states.get(before_tick)
        current = pre_shot_states.get(shot["tick"])
        if before is None or current is None:
            continue
        delta_pitch = current["pitch"] - before["pitch"]
        delta_yaw = (current["yaw"] - before["yaw"] + 180) % 360 - 180
        angular_change = math.hypot(delta_pitch, delta_yaw)
        angular_deviation_by_tick[shot["tick"]] = angular_change
        angular_velocity_by_tick[shot["tick"]] = (
            angular_change * tick_rate / ANGULAR_LOOKBACK_TICKS
        )

    shots_with_velocity = target_shots.join(
        snapshots.select("tick", "steamid", "velocity"),
        on=["tick", "steamid"],
        how="left",
    )
    rifle_total, rifle_moving_count, rifle_moving_percentage, moving_shots = calculate_weapon_metrics(
        shots_with_velocity, RIFLE_WEAPONS
    )
    sniper_total, sniper_moving_count, sniper_moving_percentage, _ = calculate_weapon_metrics(
        shots_with_velocity, SNIPER_WEAPONS
    )
    smg_total, smg_moving_count, smg_moving_percentage, _ = calculate_weapon_metrics(
        shots_with_velocity, SMG_WEAPONS
    )
    pistol_total, pistol_moving_count, pistol_moving_percentage, _ = calculate_weapon_metrics(
        shots_with_velocity, PISTOL_WEAPONS
    )
    deagle_usp_moving_total, deagle_usp_moving_count, deagle_usp_moving_percentage, _ = calculate_weapon_metrics(
        shots_with_velocity, DEAGLE_USP
    )
    awp_unscoped_shots = target_shots.filter(
        (pl.col("weapon") == "weapon_awp") & (pl.col("scoped") == False)
    ).height

    velocity_75_100 = moving_shots.filter(pl.col("velocity") <= 100).height
    velocity_100_150 = moving_shots.filter(
        (pl.col("velocity") > 100) & (pl.col("velocity") <= 150)
    ).height
    velocity_over_150 = moving_shots.filter(pl.col("velocity") > 150).height
    over_150_shots = moving_shots.filter(pl.col("velocity") > 150).select("tick", "weapon")
    moving_percentage = (
        rifle_moving_count / rifle_total * 100 if rifle_total else 0.0
    )

    return {
        "angular_velocity_by_tick": angular_velocity_by_tick,
        "angular_deviation_by_tick": angular_deviation_by_tick,
        "shots_with_velocity": shots_with_velocity,
        "rifle_total": rifle_total,
        "rifle_moving_count": rifle_moving_count,
        "rifle_moving_percentage": rifle_moving_percentage,
        "moving_shots": moving_shots,
        "sniper_total": sniper_total,
        "sniper_moving_count": sniper_moving_count,
        "sniper_moving_percentage": sniper_moving_percentage,
        "smg_total": smg_total,
        "smg_moving_count": smg_moving_count,
        "smg_moving_percentage": smg_moving_percentage,
        "pistol_total": pistol_total,
        "pistol_moving_count": pistol_moving_count,
        "pistol_moving_percentage": pistol_moving_percentage,
        "deagle_usp_moving_total": deagle_usp_moving_total,
        "deagle_usp_moving_count": deagle_usp_moving_count,
        "deagle_usp_moving_percentage": deagle_usp_moving_percentage,
        "awp_unscoped_shots": awp_unscoped_shots,
        "velocity_75_100": velocity_75_100,
        "velocity_100_150": velocity_100_150,
        "velocity_over_150": velocity_over_150,
        "over_150_shots": over_150_shots,
        "moving_percentage": moving_percentage,
        "total_shots_count": rifle_total,
        "moving_shots_count": rifle_moving_count,
    }
