"""Shared report context, diagnosis rules, and text details."""

from html import escape

import polars as pl

from .constants import RIFLE_WEAPONS, WEAPON_LABELS
from .localization import translate
from .rendering.charts import render_velocity_chart
from .rendering.html import render_diagnosis_cards


def get_qualitative_label(value, label_type: str, locale: str = "en") -> str:
    """Returns a qualitative description for a given metric."""
    band = "steady"
    if label_type == "kd":
        metric = "kd"
        band = "low" if value < 1.0 else "high" if value > 1.5 else "steady"
    elif label_type == "adr":
        metric = "adr"
        band = "low" if value < 60 else "high" if value > 80 else "steady"
    elif label_type == "kast":
        metric = "kast"
        band = "low" if value < 60 else "high" if value > 75 else "steady"
    elif label_type == "hs":
        metric = "headshot"
        band = "low" if value < 20 else "high" if value > 30 else "steady"
    elif label_type == "accuracy":
        metric = "accuracy"
        band = "low" if value < 15 else "high" if value > 30 else "steady"
    else:
        return ""
    return translate(locale, f"quality.{metric}.{band}")




def number(value, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def headshot_percentage(hit_data: dict) -> float:
    total = sum(item["total"] for item in hit_data.values())
    heads = sum(item["counts"].get("head", 0) for item in hit_data.values())
    return heads / total * 100 if total else 0.0


def _flash_result_key(result: str) -> str:
    return {
        "blinded no one": "no_one",
        "teammates only": "teammates_only",
        "enemy blinded": "enemy",
        "self-blind only": "self_only",
    }.get(result, "no_one")


def _playstyle_messages(movement: dict, aim: dict, locale: str) -> list[tuple]:
    messages = []
    if movement["rifle_total"] >= 5 and movement["rifle_moving_percentage"] > 15:
        messages.append((
            "warning-red",
            translate(locale, "diagnosis.rifle_moving", percentage=movement["rifle_moving_percentage"]),
        ))
    if movement["sniper_total"] >= 5 and movement["sniper_moving_percentage"] > 10:
        messages.append((
            "warning-red",
            translate(locale, "diagnosis.sniper_moving", percentage=movement["sniper_moving_percentage"]),
        ))
    if movement["sniper_total"] >= 5 and movement["awp_unscoped_shots"] > 1:
        messages.append((
            "warning-yellow",
            translate(locale, "diagnosis.awp_unscoped", count=movement["awp_unscoped_shots"]),
        ))
    if movement["smg_total"] >= 5 and movement["smg_moving_percentage"] < 30:
        messages.append((
            "warning-yellow",
            translate(locale, "diagnosis.submachine_gun_low_moving", percentage=movement["smg_moving_percentage"]),
            "weapon-visuals",
        ))
    elif movement["smg_total"] >= 5 and movement["smg_moving_percentage"] > 80:
        messages.append((
            "note-gentle",
            translate(locale, "diagnosis.submachine_gun_high_moving"),
            "weapon-visuals",
        ))
    distance = aim["average_fiveseven_tec9_distance"]
    if movement["pistol_total"] >= 5 and distance is not None and distance > 800:
        messages.append((
            "warning-orange",
            translate(locale, "diagnosis.pistol_long_range", count=aim["fiveseven_tec9_long_kills"]),
        ))
    if movement["pistol_total"] >= 5 and movement["deagle_usp_moving_percentage"] > 20:
        messages.append((
            "warning-yellow",
            translate(locale, "diagnosis.deagle_usp_moving", percentage=movement["deagle_usp_moving_percentage"]),
        ))
    return messages


def _diagnosis_messages(target_shots, hit_data: dict, movement: dict, flashes: dict, locale: str) -> list[tuple]:
    messages = []
    flash_harms_team = flashes["flash_teammate_or_self_count"]
    if flash_harms_team:
        messages.append((
            "warning-red",
            translate(locale, "diagnosis.flash_team_harm", throws=flashes["flash_count"], harmful=flash_harms_team),
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
                translate(locale, "diagnosis.rifle_body_hits", weapon=label, percentage=body_rate),
                "weapon-visuals",
            ))
    return messages


def build_report_context(
    *, demo_path, demo, player_name: str, player_stats: dict, target_shots,
    hit_analysis: dict, movement: dict, aim: dict, flashes: dict,
    utility_deaths, archetype_analysis: dict, locale: str = "en",
) -> dict:
    """Prepare shared presentation values used by both report versions."""
    hit_data = hit_analysis["hit_model_data"]
    kills = int(number(player_stats.get("kills")))
    deaths = int(number(player_stats.get("deaths")))
    kd_display = f"{kills / deaths:.2f}" if deaths else f"{kills:.2f}"
    adr_display = f"{number(player_stats.get('adr')):.1f}"
    kast_display = f"{number(player_stats.get('kast')):.1f}%"
    hs_display = f"{number(player_stats.get('headshot_pct')):.1f}%"
    accuracy_display = f"{number(player_stats.get('accuracy')):.1f}%"

    stats_cards = "".join((
        f'<div class="stat-card"><span class="stat-label">{escape(translate(locale, "stat.kd"))}</span><strong>{kd_display}</strong> <small>({escape(get_qualitative_label(kills / deaths if deaths else kills, "kd", locale))})</small></div>',
        f'<div class="stat-card"><span class="stat-label">{escape(translate(locale, "stat.adr"))}</span><strong>{adr_display}</strong> <small>({escape(get_qualitative_label(number(player_stats.get("adr")), "adr", locale))})</small></div>',
        f'<div class="stat-card"><span class="stat-label">{escape(translate(locale, "stat.kast"))}</span><strong>{kast_display}</strong> <small>({escape(get_qualitative_label(number(player_stats.get("kast")), "kast", locale))})</small></div>',
        f'<div class="stat-card"><span class="stat-label">{escape(translate(locale, "stat.headshot"))}</span><strong>{hs_display}</strong> <small>({escape(get_qualitative_label(number(player_stats.get("headshot_pct")), "hs", locale))})</small></div>',
        f'<div class="stat-card"><span class="stat-label">{escape(translate(locale, "stat.accuracy"))}</span><strong>{accuracy_display}</strong> <small>({escape(get_qualitative_label(number(player_stats.get("accuracy")), "accuracy", locale))})</small></div>',
    ))
    categories = (
        (translate(locale, "category.rifle"), "rifle_total", "rifle_moving_count", "rifle_moving_percentage"),
        (translate(locale, "category.sniper"), "sniper_total", "sniper_moving_count", "sniper_moving_percentage"),
        (translate(locale, "category.submachine_gun"), "smg_total", "smg_moving_count", "smg_moving_percentage"),
        (translate(locale, "category.pistol"), "pistol_total", "pistol_moving_count", "pistol_moving_percentage"),
    )
    playstyle_rows = "".join(
        f"<tr><td>{label}</td><td>{movement[total]}</td><td>{movement[moving]}</td><td>{movement[rate]:.1f}%</td></tr>"
        for label, total, moving, rate in categories
    )
    weapon_rows = "".join(
        f'<tr><td>{escape(WEAPON_LABELS.get(str(row["weapon"]).removeprefix("weapon_"), str(row["weapon"])))}</td>'
        f'<td>{row["average"]:.2f} {escape(translate(locale, "unit.degrees"))}</td><td>{row["count"]}</td></tr>'
        for row in aim["weapon_deviation_summary"]
    )
    flash_row_html = []
    for row in flashes["flash_details"]:
        result = translate(locale, f"flash.result.{_flash_result_key(row['result'])}")
        flash_row_html.append(
            f'<tr><td>{row["enemies"]}</td><td>{row["teammates"]}</td>'
            f'<td>{row["self"]}</td><td>{escape(result)}</td></tr>'
        )
    flash_rows = "".join(flash_row_html)
    suspected_count = len(aim["shots_before_crosshair_settles"])
    suspected_sentence = (
        translate(locale, "text.crosshair_settling_one")
        if suspected_count == 1
        else translate(locale, "text.crosshair_settling_many", count=suspected_count)
        if suspected_count else ""
    )
    suspected_section = (
        f'<section><h2>{escape(translate(locale, "report.v1.suspected_fire"))}</h2><p>{escape(suspected_sentence)}</p></section>'
        if suspected_sentence else ""
    )

    messages = _diagnosis_messages(target_shots, hit_data, movement, flashes, locale)
    messages.extend(_playstyle_messages(movement, aim, locale))
    if not messages:
        messages.append((
            "hint-gray",
            translate(locale, "diagnosis.no_obvious_errors"),
        ))
    summary = [
        translate(locale, "summary.rifle_moving", moving=movement["rifle_moving_count"], total=movement["rifle_total"], percentage=movement["rifle_moving_percentage"]),
        translate(locale, "summary.flash", throws=flashes["flash_count"], enemies=flashes["enemy_blinds"], teammates=flashes["teammate_blinds"]),
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
        "diagnosis_html": f'<div class="diagnosis-grid">{render_diagnosis_cards(messages, locale)}</div>',
        "diagnosis_messages": messages,
        "summary_sentences": summary,
        "hit_model_html": hit_analysis["hit_model_html"],
        "weapon_playstyle_rows": playstyle_rows,
        "weapon_deviation_rows": weapon_rows,
        "flash_detail_rows": flash_rows,
        "suspected_fire_section_html": suspected_section,
        "suspected_fire_sentence": suspected_sentence,
        "chart_html": render_velocity_chart(
            movement["velocity_75_100"],
            movement["velocity_100_150"],
            movement["velocity_over_150"],
            locale=locale,
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
        "locale": locale,
    }


def common_text_lines(context: dict) -> list[str]:
    """Return the shared detailed text portion of either report."""
    movement = context["movement"]
    aim = context["aim"]
    flashes = context["flash_analysis"]
    locale = context.get("locale", "en")
    average = aim["average_kill_deviation"]
    lines = [
        translate(locale, "text.match_details"),
        f"{translate(locale, 'text.player')}: {context['target_player']}",
        f"{translate(locale, 'text.demo')}: {context['demo_path'].name}",
        f"{translate(locale, 'text.utility_deaths')} {context['utility_deaths'].height}",
        "",
        translate(locale, "text.aim_deviation"),
        translate(locale, "text.average_deviation", degrees=f"{average:.2f}") if average is not None else translate(locale, "text.average_deviation_unavailable"),
        translate(locale, "text.by_weapon"),
    ]
    for row in aim["weapon_deviation_summary"]:
        label = WEAPON_LABELS.get(str(row["weapon"]).removeprefix("weapon_"), str(row["weapon"]))
        lines.append(translate(locale, "text.weapon_deviation", weapon=label, average=f"{row['average']:.2f}", count=row["count"]))
    lines.extend((
        "", translate(locale, "text.weapon_movement"),
        translate(locale, "text.movement_line", category=translate(locale, "category.rifle"), moving=movement["rifle_moving_count"], total=movement["rifle_total"], percentage=movement["rifle_moving_percentage"]),
        translate(locale, "text.movement_line", category=translate(locale, "category.submachine_gun"), moving=movement["smg_moving_count"], total=movement["smg_total"], percentage=movement["smg_moving_percentage"]),
        translate(locale, "text.movement_line", category=translate(locale, "category.pistol"), moving=movement["pistol_moving_count"], total=movement["pistol_total"], percentage=movement["pistol_moving_percentage"]),
        translate(locale, "text.movement_line", category=translate(locale, "category.sniper"), moving=movement["sniper_moving_count"], total=movement["sniper_total"], percentage=movement["sniper_moving_percentage"]),
    ))
    if context["suspected_fire_sentence"]:
        lines.append(context["suspected_fire_sentence"])
    lines.extend((
        "", translate(locale, "text.flashbangs"),
        f'{translate(locale, "text.thrown")} {flashes["flash_count"]}',
        f'{translate(locale, "text.enemies_blinded")} {flashes["enemy_blinds"]}',
        f'{translate(locale, "text.teammates_blinded")} {flashes["teammate_blinds"]}',
        f'{translate(locale, "text.self_blinds")} {flashes["self_blinds"]}',
    ))
    for index, row in enumerate(flashes["flash_details"], start=1):
        result = translate(locale, f"flash.result.{_flash_result_key(row['result'])}")
        lines.append(translate(locale, "text.flash_detail", index=index, enemies=row["enemies"], teammates=row["teammates"], self_blinds=row["self"], result=result))
    return lines
