"""Shared report context, diagnosis rules, and text details."""

from html import escape

import polars as pl

from .constants import RIFLE_WEAPONS, WEAPON_LABELS
from .rendering.charts import render_velocity_chart
from .rendering.html import render_diagnosis_cards


def number(value, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def headshot_percentage(hit_data: dict) -> float:
    total = sum(item["total"] for item in hit_data.values())
    heads = sum(item["counts"].get("head", 0) for item in hit_data.values())
    return heads / total * 100 if total else 0.0


def _playstyle_messages(movement: dict, aim: dict) -> list[tuple]:
    messages = []
    if movement["rifle_total"] >= 5 and movement["rifle_moving_percentage"] > 15:
        messages.append((
            "warning-red",
            f"You fired {movement['rifle_moving_percentage']:.1f}% of your rifle shots while moving. Rifles are inaccurate when moving—make sure you stop completely before shooting.",
        ))
    if movement["sniper_total"] >= 5 and movement["sniper_moving_percentage"] > 10:
        messages.append((
            "warning-red",
            f"You fired {movement['sniper_moving_percentage']:.1f}% of your sniper shots while moving. Make sure you're fully stopped before firing.",
        ))
    if movement["sniper_total"] >= 5 and movement["awp_unscoped_shots"] > 1:
        messages.append((
            "warning-yellow",
            f"You fired {movement['awp_unscoped_shots']} AWP shots without scoping. Make sure you're scoped before shooting.",
        ))
    if movement["smg_total"] >= 5 and movement["smg_moving_percentage"] < 30:
        messages.append((
            "warning-yellow",
            f"You only moved during {movement['smg_moving_percentage']:.1f}% of your SMG shots. Use your speed to make yourself a harder target.",
            "weapon-visuals",
        ))
    elif movement["smg_total"] >= 5 and movement["smg_moving_percentage"] > 80:
        messages.append((
            "note-gentle",
            "You're running and gunning almost every SMG fight. Close the distance before taking long-range fights.",
            "weapon-visuals",
        ))
    distance = aim["average_fiveseven_tec9_distance"]
    if movement["pistol_total"] >= 5 and distance is not None and distance > 800:
        messages.append((
            "warning-orange",
            f"You took {aim['fiveseven_tec9_long_kills']} long-range kills with the Five-SeveN/Tec-9. Try to play closer to cover.",
        ))
    if movement["pistol_total"] >= 5 and movement["deagle_usp_moving_percentage"] > 20:
        messages.append((
            "warning-yellow",
            f"You fired {movement['deagle_usp_moving_percentage']:.1f}% of your Deagle/USP shots while moving. Try to be stationary when you shoot.",
        ))
    return messages


def _diagnosis_messages(target_shots, hit_data: dict, movement: dict, flashes: dict) -> list[tuple]:
    messages = []
    flash_harms_team = flashes["flash_teammate_or_self_count"]
    if flash_harms_team:
        messages.append((
            "warning-red",
            f"You threw {flashes['flash_count']} flashes this match, {flash_harms_team} of which caused teammate or self-blindness. Check the timing and lineups of your flashes—they may be affecting teammates.",
            "flashbang-table",
        ))

    rifle_counts = (
        target_shots.filter(pl.col("weapon").is_in(RIFLE_WEAPONS))
        .group_by("weapon").len().sort(["len", "weapon"], descending=[True, False])
    )
    if not rifle_counts.is_empty() and movement["rifle_total"] >= 5:
        weapon = rifle_counts.item(0, "weapon").removeprefix("weapon_")
        weapon_data = hit_data.get(weapon, {})
        counts = weapon_data.get("counts", {})
        total = weapon_data.get("total", 0)
        body_count = counts.get("chest", 0) + counts.get("stomach", 0)
        body_rate = body_count / total * 100 if total else 0
        if total >= 5 and body_rate > 60:
            label = WEAPON_LABELS.get(weapon, weapon)
            messages.append((
                "warning-yellow",
                f"Your {label} hit the chest or stomach on {body_rate:.1f}% of recorded hits. Start your spray at head level and check the weapon visual below.",
                "weapon-visuals",
            ))
    return messages


def build_report_context(
    *, demo_path, demo, player_name: str, player_stats: dict, target_shots,
    hit_analysis: dict, movement: dict, aim: dict, flashes: dict,
    utility_deaths, archetype_analysis: dict,
) -> dict:
    """Prepare shared presentation values used by both report versions."""
    hit_data = hit_analysis["hit_model_data"]
    kills = int(number(player_stats.get("kills")))
    deaths = int(number(player_stats.get("deaths")))
    kd_display = f"{kills / deaths:.2f}" if deaths else f"{kills:.2f}"
    stats_cards = "".join((
        f'<div class="stat-card"><span class="stat-label">K/D</span><strong>{kd_display}</strong></div>',
        f'<div class="stat-card"><span class="stat-label">ADR</span><strong>{number(player_stats.get("adr")):.1f}</strong></div>',
        f'<div class="stat-card"><span class="stat-label">KAST</span><strong>{number(player_stats.get("kast")):.1f}%</strong></div>',
        f'<div class="stat-card"><span class="stat-label">HS%</span><strong>{number(player_stats.get("headshot_pct")):.1f}%</strong></div>',
    ))
    categories = (
        ("Rifle", "rifle_total", "rifle_moving_count", "rifle_moving_percentage"),
        ("Sniper (AWP/SSG08)", "sniper_total", "sniper_moving_count", "sniper_moving_percentage"),
        ("SMG", "smg_total", "smg_moving_count", "smg_moving_percentage"),
        ("Pistol", "pistol_total", "pistol_moving_count", "pistol_moving_percentage"),
    )
    playstyle_rows = "".join(
        f"<tr><td>{label}</td><td>{movement[total]}</td><td>{movement[moving]}</td><td>{movement[rate]:.1f}%</td></tr>"
        for label, total, moving, rate in categories
    )
    weapon_rows = "".join(
        f'<tr><td>{escape(WEAPON_LABELS.get(str(row["weapon"]).removeprefix("weapon_"), str(row["weapon"])))}</td>'
        f'<td>{row["average"]:.2f} degrees</td><td>{row["count"]}</td></tr>'
        for row in aim["weapon_deviation_summary"]
    )
    flash_rows = "".join(
        f'<tr><td>{row["enemies"]}</td><td>{row["teammates"]}</td>'
        f'<td>{row["self"]}</td><td>{escape(row["result"])}</td></tr>'
        for row in flashes["flash_details"]
    )
    suspected_count = len(aim["shots_before_crosshair_settles"])
    suspected_sentence = (
        f"You fired before your crosshair settled on the enemy {suspected_count} "
        f"{'time' if suspected_count == 1 else 'times'}. Try to stop your mouse before clicking."
        if suspected_count else ""
    )
    suspected_section = (
        f'<section><h2>Suspected firing before crosshair settles</h2><p>{escape(suspected_sentence)}</p></section>'
        if suspected_sentence else ""
    )

    messages = _diagnosis_messages(target_shots, hit_data, movement, flashes)
    messages.extend(_playstyle_messages(movement, aim))
    if not messages:
        messages.append((
            "hint-gray",
            "This match's data doesn't show obvious habitual errors. Keep watching multiple matches to see if patterns emerge.",
        ))
    summary = [
        f'{movement["rifle_moving_count"]} of {movement["rifle_total"]} rifle shots were fired while moving ({movement["rifle_moving_percentage"]:.1f}%).',
        f'{flashes["flash_count"]} flashes thrown; {flashes["enemy_blinds"]} enemies blinded; {flashes["teammate_blinds"]} teammates blinded.',
    ]
    summary.extend(message[1] for message in messages)
    pistol_distance = aim["average_pistol_kill_distance"]
    average_deviation = aim["average_kill_deviation"]

    return {
        "demo_path": demo_path,
        "target_player": player_name,
        "map_name": str(demo.header.get("map_name", "Unknown map")),
        "player_stats": player_stats,
        "utility_deaths": utility_deaths,
        "flash_analysis": flashes,
        "flash_count": flashes["flash_count"],
        "enemy_blinds": flashes["enemy_blinds"],
        "teammate_blinds": flashes["teammate_blinds"],
        "self_blinds": flashes["self_blinds"],
        "flashes_blinding_no_one": flashes["flashes_blinding_no_one"],
        "stats_cards": stats_cards,
        "diagnosis_html": f'<div class="diagnosis-grid">{render_diagnosis_cards(messages)}</div>',
        "diagnosis_messages": messages,
        "summary_sentences": summary,
        "hit_model_html": hit_analysis["hit_model_html"],
        "weapon_playstyle_rows": playstyle_rows,
        "weapon_deviation_rows": weapon_rows,
        "flash_detail_rows": flash_rows,
        "suspected_fire_section_html": suspected_section,
        "suspected_fire_sentence": suspected_sentence,
        "chart_html": render_velocity_chart(
            movement["velocity_75_100"], movement["velocity_100_150"], movement["velocity_over_150"]
        ),
        "average_deviation_html": f"{average_deviation:.2f}" if average_deviation is not None else "N/A",
        "average_kill_deviation": average_deviation,
        "average_pistol_kill_distance": pistol_distance,
        "pistol_distance_display": f"{pistol_distance:.1f} units" if pistol_distance is not None else "N/A",
        "pistol_distance_buckets": aim["pistol_distance_buckets"],
        "average_fiveseven_tec9_distance": aim["average_fiveseven_tec9_distance"],
        "fiveseven_tec9_long_kills": aim["fiveseven_tec9_long_kills"],
        "movement": movement,
        "aim": aim,
        "archetype_analysis": archetype_analysis,
    }


def common_text_lines(context: dict) -> list[str]:
    """Return the shared detailed text portion of either report."""
    movement = context["movement"]
    aim = context["aim"]
    flashes = context["flash_analysis"]
    average = aim["average_kill_deviation"]
    lines = [
        "MATCH DETAILS",
        f"Player: {context['target_player']}",
        f"Demo: {context['demo_path'].name}",
        f"Deaths while holding utility: {context['utility_deaths'].height}",
        "",
        "AIM DEVIATION ON KILLS",
        f"Average deviation: {average:.2f} degrees (lower is better)." if average is not None else "Average deviation: unavailable.",
        "By weapon (average deviation, sample count):",
    ]
    for row in aim["weapon_deviation_summary"]:
        label = WEAPON_LABELS.get(str(row["weapon"]).removeprefix("weapon_"), str(row["weapon"]))
        lines.append(f"  {label}: {row['average']:.2f} degrees across {row['count']} kills")
    lines.extend((
        "", "WEAPON MOVEMENT",
        f'Rifles: {movement["rifle_moving_count"]}/{movement["rifle_total"]} moving ({movement["rifle_moving_percentage"]:.1f}%)',
        f'SMGs: {movement["smg_moving_count"]}/{movement["smg_total"]} moving ({movement["smg_moving_percentage"]:.1f}%)',
        f'Pistols: {movement["pistol_moving_count"]}/{movement["pistol_total"]} moving ({movement["pistol_moving_percentage"]:.1f}%)',
        f'Snipers: {movement["sniper_moving_count"]}/{movement["sniper_total"]} moving ({movement["sniper_moving_percentage"]:.1f}%)',
    ))
    if context["suspected_fire_sentence"]:
        lines.append(context["suspected_fire_sentence"])
    lines.extend((
        "", "FLASHBANGS", f'Thrown: {flashes["flash_count"]}',
        f'Enemies blinded: {flashes["enemy_blinds"]}',
        f'Teammates blinded: {flashes["teammate_blinds"]}',
        f'Self-blinds: {flashes["self_blinds"]}',
    ))
    for index, row in enumerate(flashes["flash_details"], start=1):
        lines.append(
            f'  Flash {index}: {row["enemies"]} enemies, {row["teammates"]} teammates, '
            f'{row["self"]} self-blinds — {row["result"]}'
        )
    return lines
