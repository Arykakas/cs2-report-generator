from pathlib import Path
import argparse
from html import escape

import polars as pl

from .analysis.aim import analyze_aim
from .analysis.flashes import analyze_flashes
from .analysis.hits import analyze_hits
from .analysis.utility_deaths import analyze_utility_deaths
from .analysis.weapons import analyze_weapon_movement
from .demo import load_demo, resolve_player
from .rendering.charts import render_velocity_chart
from .rendering.html import render_html_report


from .constants import (
    ANGULAR_LOOKBACK_TICKS,
    ANGULAR_VELOCITY_THRESHOLD_DPS,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a CS2 demo post-match report.")
    parser.add_argument("--demo", required=True, type=Path, help="Path to the .dem file")
    parser.add_argument("--player", required=True, help="Player name or SteamID64")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    demo_path = args.demo.expanduser().resolve()
    player_input = args.player.strip()
    demo = load_demo(demo_path)
    player_steamid, target_player, target_shots = resolve_player(demo, player_input)

    hit_model_html = analyze_hits(demo, player_steamid)["hit_model_html"]

    movement = analyze_weapon_movement(demo, target_shots, player_steamid)
    angular_velocity_by_tick = movement["angular_velocity_by_tick"]
    angular_deviation_by_tick = movement["angular_deviation_by_tick"]
    shots_with_velocity = movement["shots_with_velocity"]
    rifle_total = movement["rifle_total"]
    rifle_moving_count = movement["rifle_moving_count"]
    rifle_moving_percentage = movement["rifle_moving_percentage"]
    moving_shots = movement["moving_shots"]
    sniper_total = movement["sniper_total"]
    sniper_moving_count = movement["sniper_moving_count"]
    sniper_moving_percentage = movement["sniper_moving_percentage"]
    smg_total = movement["smg_total"]
    smg_moving_count = movement["smg_moving_count"]
    smg_moving_percentage = movement["smg_moving_percentage"]
    pistol_total = movement["pistol_total"]
    pistol_moving_count = movement["pistol_moving_count"]
    pistol_moving_percentage = movement["pistol_moving_percentage"]
    deagle_usp_moving_percentage = movement["deagle_usp_moving_percentage"]
    awp_unscoped_shots = movement["awp_unscoped_shots"]
    velocity_75_100 = movement["velocity_75_100"]
    velocity_100_150 = movement["velocity_100_150"]
    velocity_over_150 = movement["velocity_over_150"]
    over_150_shots = movement["over_150_shots"]
    moving_percentage = movement["moving_percentage"]
    total_shots_count = movement["total_shots_count"]
    moving_shots_count = movement["moving_shots_count"]

    utility_result = analyze_utility_deaths(demo, target_player)
    utility_deaths = utility_result["utility_deaths"]
    utility_death_ticks = utility_result["utility_death_ticks"]

    aim = analyze_aim(demo, target_shots, player_steamid, angular_velocity_by_tick,
                      angular_deviation_by_tick, shots_with_velocity)
    kill_deviations = aim["kill_deviations"]
    average_kill_deviation = aim["average_kill_deviation"]
    average_pistol_kill_distance = aim["average_pistol_kill_distance"]
    pistol_distance_buckets = aim["pistol_distance_buckets"]
    average_fiveseven_tec9_distance = aim["average_fiveseven_tec9_distance"]
    fiveseven_tec9_long_kills = aim["fiveseven_tec9_long_kills"]
    ak_avg_pitch_bias = aim["ak_avg_pitch_bias"]
    ak_high_deviation_kill_count = aim["ak_high_deviation_kill_count"]
    weapon_deviation_summary = aim["weapon_deviation_summary"]
    high_deviation_kills = aim["high_deviation_kills"]
    shots_before_crosshair_settles = aim["shots_before_crosshair_settles"]

    flash_analysis = analyze_flashes(demo, player_steamid)
    flash_count = flash_analysis["flash_count"]
    enemy_blinds = flash_analysis["enemy_blinds"]
    teammate_blinds = flash_analysis["teammate_blinds"]
    self_blinds = flash_analysis["self_blinds"]
    teammate_only_flashes = flash_analysis["teammate_only_flashes"]
    flashes_blinding_no_one = flash_analysis["flashes_blinding_no_one"]
    flash_teammate_or_self_count = flash_analysis["flash_teammate_or_self_count"]
    flash_details = flash_analysis["flash_details"]

    player_stats_frame = demo.stats.filter(pl.col("name") == target_player)
    if player_stats_frame.is_empty():
        raise ValueError(f"No basic stats found for player name: {target_player}")
    player_stats = player_stats_frame.row(0, named=True)
    kills = player_stats["kills"] or 0
    deaths = player_stats["deaths"] or 0
    kd_ratio = kills / deaths if deaths else float(kills)

    chart_html = render_velocity_chart(
        velocity_75_100, velocity_100_150, velocity_over_150
    )

    kd_display = f"{kd_ratio:.2f}"
    playstyle_messages = []
    if rifle_moving_percentage > 15:
        playstyle_messages.append(
            (
                "warning-red",
                f"You fired {rifle_moving_percentage:.1f}% of your rifle shots while moving. Rifles are inaccurate when moving—make sure you stop completely before shooting.",
            )
        )
    if sniper_moving_percentage > 10:
        playstyle_messages.append(
            (
                "warning-red",
                f"You fired {sniper_moving_percentage:.1f}% of your sniper shots while moving. Snipers are the least forgiving for movement—even walking makes the shot miss. Make sure you're fully stopped before firing.",
            )
        )
    if awp_unscoped_shots > 1:
        playstyle_messages.append(
            (
                "warning-yellow",
                f"You fired {awp_unscoped_shots} AWP shots without scoping. Unless it's point-blank, this is unreliable. Make sure you're scoped in before you shoot.",
            )
        )
    if smg_total and smg_moving_percentage < 30:
        playstyle_messages.append(
            (
                "warning-yellow",
                f"You only moved during {smg_moving_percentage:.1f}% of your SMG shots. SMGs are accurate while running—don't play them like a rifle. Use your speed to make yourself a harder target.",
            )
        )
    elif smg_total and smg_moving_percentage > 80:
        playstyle_messages.append(
            (
                "note-gentle",
                "You're running and gunning almost every SMG fight. Great for close range, but at long range you'll lose to rifles—try to close the distance first.",
            )
        )
    if (
        average_fiveseven_tec9_distance is not None
        and average_fiveseven_tec9_distance > 800
    ):
        playstyle_messages.append(
            (
                "warning-orange",
                f"You took {fiveseven_tec9_long_kills} long-range kills with the Five-SeveN/Tec-9. It's deadly up close but loses to rifles at long range—try to play closer to cover.",
            )
        )
    if deagle_usp_moving_percentage > 20:
        playstyle_messages.append(
            (
                "warning-yellow",
                f"You fired {deagle_usp_moving_percentage:.1f}% of your Deagle/USP shots while moving. These are precision weapons—make sure you're stationary when you shoot.",
            )
        )
    playstyle_html = "".join(
        f'<p class="conclusion {kind}">{escape(message)}</p>'
        for kind, message in playstyle_messages
    )
    conclusion_messages = []
    if flash_teammate_or_self_count > 0:
        conclusion_messages.append(
            (
                "warning-red",
                f"You threw {flash_count} flashes this match, {flash_teammate_or_self_count} of which caused teammate or self-blindness. "
                "Check the timing and lineups of your flashes—they may be affecting teammates.",
            )
        )
    if ak_avg_pitch_bias is not None and ak_avg_pitch_bias > 5:
        conclusion_messages.append(
            (
                "warning-yellow",
                "You are pulling your AK down too much. You're aiming at the waist instead of the head. "
                "When you spray, make sure you start at head level.",
            )
        )
    if not conclusion_messages:
        conclusion_messages.append(
            (
                "hint-gray",
                "This match's data doesn't show obvious habitual errors. Keep watching multiple matches to see if patterns emerge.",
            )
        )
    conclusion_html = "".join(
        f'<p class="conclusion {kind}">{escape(message)}</p>'
        for kind, message in conclusion_messages
    )
    diagnosis_html = conclusion_html + playstyle_html
    map_name = demo.header.get("map_name", "Unknown map")
    stats_cards = "".join(
        [
            f'<div class="stat-card"><span class="stat-label">K/D</span><strong>{kd_display}</strong></div>',
            f'<div class="stat-card"><span class="stat-label">ADR</span><strong>{player_stats["adr"]:.1f}</strong></div>',
            f'<div class="stat-card"><span class="stat-label">KAST</span><strong>{player_stats["kast"]:.1f}%</strong></div>',
            f'<div class="stat-card"><span class="stat-label">HS%</span><strong>{player_stats["headshot_pct"]:.1f}%</strong></div>',
        ]
    )
    kill_deviation_rows = "".join(
        f'<tr><td>{item["kill_tick"]}</td><td>{item["shot_tick"]}</td>'
        f'<td>{escape(str(item["victim"]))}</td><td>{escape(str(item["weapon"]))}</td>'
        f'<td>{item["deviation"]:.2f} deg</td></tr>'
        for item in kill_deviations
    )
    average_deviation_html = (
        f"{average_kill_deviation:.2f} deg"
        if average_kill_deviation is not None
        else "N/A"
    )
    weapon_deviation_rows = "".join(
        f'<tr><td>{escape(item["weapon"])}</td><td>{item["average"]:.2f} deg</td>'
        f'<td>{item["count"]}</td></tr>'
        for item in weapon_deviation_summary
    )
    high_deviation_rows = "".join(
        f'<tr><td>{item["kill_tick"]}</td><td>{escape(str(item["victim"]))}</td>'
        f'<td>{item["deviation"]:.2f} deg</td><td>{item["firing_pitch"]:.2f}</td>'
        f'<td>{item["firing_yaw"]:.2f}</td><td>{item["victim_pitch"]:.2f}</td>'
        f'<td>{item["victim_yaw"]:.2f}</td></tr>'
        for item in high_deviation_kills
    )
    suspected_fire_rows = "".join(
        f'<tr><td>{item["shot_tick"]}</td><td>{escape(item["weapon"])}</td>'
        f'<td>{item["angular_velocity"]:.1f} deg/s</td><td>{item["angular_deviation"]:.2f} deg</td>'
        f'<td>{"Yes" if item["hit"] else "No"}</td></tr>'
        for item in shots_before_crosshair_settles
    )
    flash_detail_rows = "".join(
        f'<tr><td>{item["detonation_tick"]}</td><td>{item["enemies"]}</td>'
        f'<td>{item["teammates"]}</td><td>{item["self"]}</td>'
        f'<td>{escape(item["result"])}</td></tr>'
        for item in flash_details
    )
    weapon_playstyle_rows = "".join(
        [
            f"<tr><td>Rifle</td><td>{rifle_total}</td><td>{rifle_moving_count}</td><td>{rifle_moving_percentage:.1f}%</td></tr>",
            f"<tr><td>Sniper (AWP/SSG08)</td><td>{sniper_total}</td><td>{sniper_moving_count}</td><td>{sniper_moving_percentage:.1f}%</td></tr>",
            f"<tr><td>SMG</td><td>{smg_total}</td><td>{smg_moving_count}</td><td>{smg_moving_percentage:.1f}%</td></tr>",
            f"<tr><td>Pistol</td><td>{pistol_total}</td><td>{pistol_moving_count}</td><td>{pistol_moving_percentage:.1f}%</td></tr>",
        ]
    )
    summary_sentences = [
        f"{moving_shots_count} of {total_shots_count} rifle shots were fired while moving ({moving_percentage:.1f}%).",
        f"Shots fired before the crosshair settled: {len(shots_before_crosshair_settles)} above {ANGULAR_VELOCITY_THRESHOLD_DPS:.0f} deg/s over a {ANGULAR_LOOKBACK_TICKS}-tick window.",
        f"Flashbangs: {flash_count} thrown; {enemy_blinds} enemies and {teammate_blinds} teammates blinded; {teammate_only_flashes} blinded teammates only; {flashes_blinding_no_one} blinded no one.",
    ]
    summary_sentences.extend(message for _, message in playstyle_messages)
    html_report = render_html_report(globals() | locals())

    report_lines = [
        "SUMMARY",
        *summary_sentences,
        "",
        "DETAILED DATA",
        f"Player: {target_player}",
        f"Demo: {demo_path}",
        f"Rifle total shots: {total_shots_count}",
        f"Rifle moving shots: {moving_shots_count}",
        f"Rifle moving shot percentage: {moving_percentage:.1f}%",
        f"Sniper total shots: {sniper_total}",
        f"Sniper moving shots: {sniper_moving_count}",
        f"Sniper moving shot percentage: {sniper_moving_percentage:.1f}%",
        f"Unscoped AWP shots: {awp_unscoped_shots}",
        f"SMG total shots: {smg_total}",
        f"SMG moving shots: {smg_moving_count}",
        f"SMG moving shot percentage: {smg_moving_percentage:.1f}%",
        f"Pistol total shots: {pistol_total}",
        f"Pistol moving shots: {pistol_moving_count}",
        f"Pistol moving shot percentage: {pistol_moving_percentage:.1f}%",
        f"Average pistol kill distance: {average_pistol_kill_distance:.1f} units" if average_pistol_kill_distance is not None else "Average pistol kill distance: N/A",
        f"Pistol kill distance buckets: close {pistol_distance_buckets['close']}, medium {pistol_distance_buckets['medium']}, long {pistol_distance_buckets['long']}",
        f"Five-SeveN/Tec-9 average kill distance: {average_fiveseven_tec9_distance:.1f} units" if average_fiveseven_tec9_distance is not None else "Five-SeveN/Tec-9 average kill distance: N/A",
        f"Moving shots, velocity 75-100: {velocity_75_100}",
        f"Moving shots, velocity >100-150: {velocity_100_150}",
        f"Moving shots, velocity >150: {velocity_over_150}",
        "Shots above 150 (tick, weapon):",
    ]
    for tick, weapon in over_150_shots.iter_rows():
        report_lines.append(f"  {tick}, {weapon}")
    report_lines.extend(
        [
            f"Deaths while holding utility: {utility_deaths.height}",
            f"Utility death ticks: {utility_death_ticks}",
        ]
    )
    report_lines.append(
        "Average aim deviation on kills: "
        + (f"{average_kill_deviation:.2f} degrees" if average_kill_deviation is not None else "N/A")
    )
    report_lines.append("Kill aim deviations (kill tick, shot tick, victim, weapon, degrees):")
    for item in kill_deviations:
        report_lines.append(
            f"  {item['kill_tick']}, {item['shot_tick']}, {item['victim']}, "
            f"{item['weapon']}, {item['deviation']:.2f}"
        )
    report_lines.append("Aim deviation by weapon (weapon, average degrees, sample count):")
    for item in weapon_deviation_summary:
        report_lines.append(
            f"  {item['weapon']}, {item['average']:.2f}, {item['count']}"
        )
    report_lines.append(
        "Kills above 10 degrees (kill tick, victim, deviation, firing pitch, firing yaw, victim pitch, victim yaw):"
    )
    for item in high_deviation_kills:
        report_lines.append(
            f"  {item['kill_tick']}, {item['victim']}, {item['deviation']:.2f}, "
            f"{item['firing_pitch']:.2f}, {item['firing_yaw']:.2f}, "
            f"{item['victim_pitch']:.2f}, {item['victim_yaw']:.2f}"
        )
    report_lines.append(
        f"Suspected firing before crosshair settles (angular window {ANGULAR_LOOKBACK_TICKS} ticks, "
        f"threshold >{ANGULAR_VELOCITY_THRESHOLD_DPS:.0f} deg/s; "
        "shot tick, weapon, angular velocity, angular deviation, hit enemy):"
    )
    for item in shots_before_crosshair_settles:
        report_lines.append(
            f"  {item['shot_tick']}, {item['weapon']}, "
            f"{item['angular_velocity']:.1f} deg/s, {item['angular_deviation']:.2f} degrees, "
            f"{'Yes' if item['hit'] else 'No'}"
        )
    report_lines.extend(
        [
            f"Flashbangs thrown: {flash_count}",
            f"Enemy blinds: {enemy_blinds}",
            f"Teammates blinded: {teammate_blinds}",
            f"Self-blinds: {self_blinds}",
            f"Flashes that blinded teammates only: {teammate_only_flashes}",
            f"Flashes that blinded no one: {flashes_blinding_no_one}",
            "Flash details (detonation tick, enemies, teammates, self, result):",
        ]
    )
    for item in flash_details:
        report_lines.append(
            f"  {item['detonation_tick']}, {item['enemies']}, {item['teammates']}, "
            f"{item['self']}, {item['result']}"
        )

    report_path = demo_path.with_name(f"{demo_path.stem}_report.txt")
    html_report_path = demo_path.with_name(f"{demo_path.stem}_report.html")
    report_text = "\n".join(report_lines)
    report_path.write_text(report_text + "\n", encoding="utf-8")
    html_report_path.write_text(html_report, encoding="utf-8")
    print(report_text)
    print(f"\nReport saved to: {report_path}")
    print(f"HTML report saved to: {html_report_path}")


if __name__ == "__main__":
    main()
