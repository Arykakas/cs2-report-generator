"""Kill aim deviation and suspected-fire calculations."""

import math

import polars as pl

from ..constants import (
    ANGULAR_VELOCITY_THRESHOLD_DPS,
    FIVESEVEN_TEC9,
    PISTOL_WEAPONS,
)


def analyze_aim(
    demo,
    target_shots: pl.DataFrame,
    player_steamid: int,
    angular_velocity_by_tick: dict,
    angular_deviation_by_tick: dict,
    shots_with_velocity: pl.DataFrame,
) -> dict:
    """Compare firing direction to victim head position and summarize aim."""
    player_firing_shots = (
        demo.shots.filter(pl.col("steamid") == player_steamid)
        .sort("tick")
        .to_dicts()
    )
    player_kills = demo.kills.filter(pl.col("attacker_steamid") == player_steamid)
    kill_deviations = []
    shots_that_killed = set()
    for kill in player_kills.to_dicts():
        prior_shots = [shot for shot in player_firing_shots if shot["tick"] <= kill["tick"]]
        if not prior_shots:
            continue
        shot = prior_shots[-1]
        shots_that_killed.add(shot["tick"])
        dx = kill["victim_x"] - shot["x"]
        dy = kill["victim_y"] - shot["y"]
        dz = (kill["victim_z"] + 64) - shot["z"]
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance == 0:
            continue

        yaw = math.radians(shot["yaw"])
        pitch = math.radians(shot["pitch"])
        aim_direction = (
            math.cos(pitch) * math.cos(yaw),
            math.cos(pitch) * math.sin(yaw),
            -math.sin(pitch),
        )
        target_direction = (dx / distance, dy / distance, dz / distance)
        dot_product = sum(a * b for a, b in zip(aim_direction, target_direction))
        deviation = math.degrees(math.acos(max(-1.0, min(1.0, dot_product))))
        horizontal_distance = math.hypot(dx, dy)
        victim_pitch = -math.degrees(math.atan2(dz, horizontal_distance))
        victim_yaw = math.degrees(math.atan2(dy, dx))
        kill_deviations.append(
            {
                "kill_tick": kill["tick"],
                "shot_tick": shot["tick"],
                "victim": kill["victim_name"],
                "weapon": shot["weapon"],
                "deviation": deviation,
                "distance": distance,
                "firing_pitch": shot["pitch"],
                "firing_yaw": shot["yaw"],
                "victim_pitch": victim_pitch,
                "victim_yaw": victim_yaw,
                "angular_velocity": angular_velocity_by_tick.get(shot["tick"]),
            }
        )

    average_kill_deviation = (
        sum(item["deviation"] for item in kill_deviations) / len(kill_deviations)
        if kill_deviations
        else None
    )
    pistol_kill_distances = [
        item for item in kill_deviations if item["weapon"] in PISTOL_WEAPONS
    ]
    average_pistol_kill_distance = (
        sum(item["distance"] for item in pistol_kill_distances) / len(pistol_kill_distances)
        if pistol_kill_distances
        else None
    )
    pistol_distance_buckets = {
        "close": sum(item["distance"] < 500 for item in pistol_kill_distances),
        "medium": sum(500 <= item["distance"] <= 1000 for item in pistol_kill_distances),
        "long": sum(item["distance"] > 1000 for item in pistol_kill_distances),
    }
    fiveseven_tec9_kills = [
        item for item in pistol_kill_distances if item["weapon"] in FIVESEVEN_TEC9
    ]
    average_fiveseven_tec9_distance = (
        sum(item["distance"] for item in fiveseven_tec9_kills) / len(fiveseven_tec9_kills)
        if fiveseven_tec9_kills
        else None
    )
    fiveseven_tec9_long_kills = sum(
        item["distance"] > 1000 for item in fiveseven_tec9_kills
    )
    ak_pitch_bias_values = [
        item["firing_pitch"] - item["victim_pitch"]
        for item in kill_deviations
        if item["weapon"] == "weapon_ak47"
    ]
    ak_avg_pitch_bias = (
        sum(ak_pitch_bias_values) / len(ak_pitch_bias_values)
        if ak_pitch_bias_values
        else None
    )
    ak_high_deviation_kill_count = sum(
        item["weapon"] == "weapon_ak47" and item["deviation"] > 13
        for item in kill_deviations
    )
    weapon_deviations = {}
    for item in kill_deviations:
        weapon_deviations.setdefault(item["weapon"], []).append(item["deviation"])
    weapon_deviation_summary = [
        {"weapon": weapon, "count": len(values), "average": sum(values) / len(values)}
        for weapon, values in sorted(weapon_deviations.items())
    ]
    high_deviation_kills = [item for item in kill_deviations if item["deviation"] > 10]
    shots_before_crosshair_settles = [
        {
            "shot_tick": shot["tick"],
            "weapon": shot["weapon"],
            "angular_velocity": angular_velocity_by_tick[shot["tick"]],
            "angular_deviation": angular_deviation_by_tick[shot["tick"]],
            "hit": shot["tick"] in shots_that_killed,
        }
        for shot in target_shots.to_dicts()
        if shot["tick"] in angular_velocity_by_tick
        and angular_velocity_by_tick[shot["tick"]] > ANGULAR_VELOCITY_THRESHOLD_DPS
    ]
    return {
        "kill_deviations": kill_deviations,
        "average_kill_deviation": average_kill_deviation,
        "average_pistol_kill_distance": average_pistol_kill_distance,
        "pistol_distance_buckets": pistol_distance_buckets,
        "average_fiveseven_tec9_distance": average_fiveseven_tec9_distance,
        "fiveseven_tec9_long_kills": fiveseven_tec9_long_kills,
        "ak_avg_pitch_bias": ak_avg_pitch_bias,
        "ak_high_deviation_kill_count": ak_high_deviation_kill_count,
        "weapon_deviation_summary": weapon_deviation_summary,
        "high_deviation_kills": high_deviation_kills,
        "shots_before_crosshair_settles": shots_before_crosshair_settles,
    }
