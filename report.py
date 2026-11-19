from pathlib import Path
import argparse
import base64
from html import escape
import json
import math
import random

import polars as pl
import plotly.graph_objects as go
from awpy import Demo


UTILITY_WEAPONS = [
    "flashbang",
    "hegrenade",
    "smokegrenade",
    "molotov",
    "incendiarygrenade",
    "decoy",
]
RIFLE_WEAPONS = [
    "weapon_ak47",
    "weapon_m4a1",
    "weapon_m4a1_silencer",
    "weapon_galilar",
    "weapon_famas",
    "weapon_sg556",
    "weapon_aug",
 ]
SNIPER_WEAPONS = ["weapon_awp", "weapon_ssg08"]
SMG_WEAPONS = [
    "weapon_mac10",
    "weapon_mp7",
    "weapon_mp9",
    "weapon_mp5sd",
    "weapon_ump45",
    "weapon_p90",
    "weapon_bizon",
]
PISTOL_WEAPONS = [
    "weapon_glock",
    "weapon_usp_silencer",
    "weapon_hkp2000",
    "weapon_p250",
    "weapon_fiveseven",
    "weapon_tec9",
    "weapon_cz75a",
    "weapon_deagle",
    "weapon_elite",
    "weapon_revolver",
]
FIVESEVEN_TEC9 = ["weapon_fiveseven", "weapon_tec9"]
DEAGLE_USP = ["weapon_deagle", "weapon_usp_silencer", "weapon_hkp2000"]
ANGULAR_LOOKBACK_TICKS = 5
ANGULAR_VELOCITY_THRESHOLD_DPS = 300.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a CS2 demo post-match report.")
    parser.add_argument("--demo", required=True, type=Path, help="Path to the .dem file")
    parser.add_argument("--player", required=True, help="Player name or SteamID64")
    return parser.parse_args()


args = parse_args()
demo_path = args.demo.expanduser().resolve()
player_input = args.player.strip()

demo = Demo(demo_path)
demo.load("shots", "kills", "grenades", "blinds")

target_shots = demo.shots.filter(pl.col("name") == player_input)

if target_shots.is_empty():
    try:
        player_steamid = int(player_input)
    except ValueError as exc:
        raise ValueError(f"No shots found for player name or Steam ID: {player_input}") from exc
    target_shots = demo.shots.filter(pl.col("steamid") == player_steamid)

if target_shots.is_empty():
    raise ValueError(f"No shots found for player name or Steam ID: {player_input}")

player_steamid = target_shots.get_column("steamid")[0]
target_player = str(target_shots.get_column("name")[0])

HITGROUP_BY_ID = {
    1: "head",
    2: "chest",
    3: "stomach",
    4: "left_arm",
    5: "right_arm",
    6: "left_leg",
    7: "right_leg",
}
BODY_PARTS = ["head", "chest", "stomach", "left_leg", "right_leg", "left_arm", "right_arm"]
WEAPON_CATEGORIES = {
    **{weapon.removeprefix("weapon_"): "Rifle" for weapon in RIFLE_WEAPONS},
    **{weapon.removeprefix("weapon_"): "SMG" for weapon in SMG_WEAPONS},
    **{weapon.removeprefix("weapon_"): "Pistol" for weapon in PISTOL_WEAPONS},
    **{weapon.removeprefix("weapon_"): "Sniper" for weapon in SNIPER_WEAPONS},
}
WEAPON_LABELS = {
    "ak47": "AK-47",
    "m4a1": "M4A1",
    "m4a1_silencer": "M4A1-S",
    "galilar": "Galil AR",
    "famas": "FAMAS",
    "sg556": "SG 553",
    "aug": "AUG",
    "mac10": "MAC-10",
    "mp7": "MP7",
    "mp9": "MP9",
    "mp5sd": "MP5-SD",
    "ump45": "UMP-45",
    "p90": "P90",
    "bizon": "PP-Bizon",
    "glock": "Glock-18",
    "usp_silencer": "USP-S",
    "hkp2000": "P2000",
    "p250": "P250",
    "fiveseven": "Five-SeveN",
    "tec9": "Tec-9",
    "cz75a": "CZ75-Auto",
    "deagle": "Desert Eagle",
    "elite": "Dual Berettas",
    "revolver": "R8 Revolver",
    "awp": "AWP",
    "ssg08": "SSG 08",
}

try:
    demo.load("damages")
    player_hits = demo.damages.filter(pl.col("attacker_steamid") == player_steamid)
except Exception:
    player_hits = demo.kills.filter(pl.col("attacker_steamid") == player_steamid)
    player_hits = player_hits.filter(pl.col("hitgroup").is_not_null())
if player_hits.is_empty():
    player_hits = demo.kills.filter(pl.col("attacker_steamid") == player_steamid)
    player_hits = player_hits.filter(pl.col("hitgroup").is_not_null())

hit_counts = {}
for hit in player_hits.to_dicts():
    raw_weapon = str(hit.get("weapon") or "").removeprefix("weapon_")
    category = WEAPON_CATEGORIES.get(raw_weapon)
    body_part = HITGROUP_BY_ID.get(hit.get("hitgroup"))
    if category is None or body_part is None:
        continue
    weapon_key = (category, raw_weapon)
    hit_counts.setdefault(weapon_key, {part: 0 for part in BODY_PARTS})
    hit_counts[weapon_key][body_part] += 1

weapon_order = {"Rifle": 0, "SMG": 1, "Pistol": 2, "Sniper": 3}
hit_weapon_keys = sorted(
    hit_counts,
    key=lambda key: (weapon_order[key[0]], WEAPON_LABELS.get(key[1], key[1])),
)
hit_model_data = {}
for category, raw_weapon in hit_weapon_keys:
    counts = hit_counts[(category, raw_weapon)]
    total = sum(counts.values())
    hit_model_data[raw_weapon] = {
        "category": category,
        "label": WEAPON_LABELS.get(raw_weapon, raw_weapon),
        "total": total,
        "counts": counts,
        "percentages": {
            part: (counts[part] / total * 100 if total else 0)
            for part in BODY_PARTS
        },
    }

default_hit_weapon = None
if hit_model_data:
    default_hit_weapon = (
        "ak47"
        if "ak47" in hit_model_data
        else max(hit_model_data, key=lambda weapon: hit_model_data[weapon]["total"])
    )
weapon_buttons_html = "".join(
    f'<button type="button" class="weapon-button{" active" if weapon == default_hit_weapon else ""}" data-weapon="{escape(weapon, quote=True)}">{escape(info["label"])}</button>'
    for weapon, info in hit_model_data.items()
)
HIT_DOT_COLORS = {
    "head": "#ef4444",
    "chest": "#f97316",
    "stomach": "#f97316",
    "left_arm": "#3b82f6",
    "right_arm": "#3b82f6",
    "left_leg": "#3b82f6",
    "right_leg": "#3b82f6",
}
BODY_ANCHORS = {
    "head": (512, 148, 24, 35),
    "chest": (512, 380, 82, 65),
    "stomach": (512, 555, 58, 38),
    "left_arm": (700, 465, 32, 125),
    "right_arm": (324, 465, 32, 125),
    "left_leg": (650, 1050, 35, 165),
    "right_leg": (374, 1050, 35, 165),
}
bullet_points_by_weapon = {}
for hit_index, hit in enumerate(player_hits.to_dicts()):
    raw_weapon = str(hit.get("weapon") or "").removeprefix("weapon_")
    body_part = HITGROUP_BY_ID.get(hit.get("hitgroup"))
    if raw_weapon not in hit_model_data or body_part is None:
        continue
    center_x, center_y, spread_x, spread_y = BODY_ANCHORS[body_part]
    rng = random.Random(f"{hit.get('tick')}:{hit.get('attacker_steamid')}:{hit.get('victim_steamid')}:{raw_weapon}:{hit_index}")
    bullet_points_by_weapon.setdefault(raw_weapon, []).append({
        "part": body_part,
        "x": round(center_x + rng.uniform(-spread_x, spread_x), 1),
        "y": round(center_y + rng.uniform(-spread_y, spread_y), 1),
        "tick": hit.get("tick"),
    })
bullet_points_json = json.dumps(bullet_points_by_weapon, separators=(",", ":"), ensure_ascii=True)
human_svg_path = Path(__file__).parent / "human_model.svg"
human_svg = human_svg_path.read_text(encoding="utf-8").replace('fill="#000000"', 'fill="#d1d5db"')
human_svg_uri = "data:image/svg+xml;base64," + base64.b64encode(human_svg.encode("utf-8")).decode("ascii")
bullet_fig = go.Figure()
bullet_fig.update_layout(
    images=[dict(source=human_svg_uri, xref="x", yref="y", x=0, y=0, sizex=1024, sizey=1536, xanchor="left", yanchor="top", sizing="stretch", opacity=1, layer="below")],
    xaxis=dict(range=[0, 1024], visible=False, showgrid=False, zeroline=False, showline=False, ticks="", showticklabels=False, fixedrange=True, domain=[0, 1], constrain="domain"),
    yaxis=dict(range=[1536, 0], visible=False, showgrid=False, zeroline=False, showline=False, ticks="", showticklabels=False, fixedrange=True, domain=[0, 1], scaleanchor="x", scaleratio=1),
    margin=dict(l=0, r=0, t=0, b=0),
    height=620,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
)
bullet_plot_html = bullet_fig.to_html(
    full_html=False,
    include_plotlyjs="cdn",
    config={"displayModeBar": False, "responsive": True},
    div_id="bullet-heatmap-chart",
)
hit_model_html = f"""
<div class="hit-model-widget">
  <div class="weapon-buttons" role="group" aria-label="Choose weapon for bullet hole heatmap">
    {weapon_buttons_html or '<span class="subtitle">No categorized hit data for this player.</span>'}
  </div>
  <div class="bullet-heatmap-stage">
    {bullet_plot_html}
  </div>
  <div class="bullet-heatmap-legend"><span><i class="dot head-dot"></i>Head</span><span><i class="dot torso-dot"></i>Chest / stomach</span><span><i class="dot limb-dot"></i>Arms / legs</span></div>
  <p class="subtitle">Each dot represents one hit. Positions are approximated by hitgroup; weapon selections update the dots immediately.</p>
</div>
<script>
const bulletPointsByWeapon = {bullet_points_json};
const bulletPartOrder = ["head", "chest", "stomach", "left_arm", "right_arm", "left_leg", "right_leg"];
const bulletPartLabels = {{head: "Head", chest: "Chest", stomach: "Stomach", left_arm: "Left arm", right_arm: "Right arm", left_leg: "Left leg", right_leg: "Right leg"}};
const bulletPartColors = {{head: "#ef4444", chest: "#f97316", stomach: "#f97316", left_arm: "#3b82f6", right_arm: "#3b82f6", left_leg: "#3b82f6", right_leg: "#3b82f6"}};
const bulletPlotLayout = {{
  images: [{{source: {json.dumps(human_svg_uri)}, xref: "x", yref: "y", x: 0, y: 0, sizex: 1024, sizey: 1536, xanchor: "left", yanchor: "top", sizing: "stretch", opacity: 1, layer: "below"}}],
  xaxis: {{range: [0, 1024], visible: false, showgrid: false, zeroline: false, showline: false, ticks: "", showticklabels: false, fixedrange: true, domain: [0, 1], constrain: "domain"}},
  yaxis: {{range: [1536, 0], visible: false, showgrid: false, zeroline: false, showline: false, ticks: "", showticklabels: false, fixedrange: true, domain: [0, 1], scaleanchor: "x", scaleratio: 1}},
  margin: {{l: 0, r: 0, t: 0, b: 0}}, height: 615,
  paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", showlegend: false
}};
function selectHitWeapon(weapon) {{
  if (!bulletPointsByWeapon[weapon]) return;
  document.querySelectorAll(".weapon-button").forEach(button => {{
    button.classList.toggle("active", button.dataset.weapon === weapon);
  }});
  const points = bulletPointsByWeapon[weapon];
  const traces = bulletPartOrder.map(part => {{
    const hits = points.filter(hit => hit.part === part);
    return {{
      type: "scatter", mode: "markers", name: bulletPartLabels[part],
      x: hits.map(hit => hit.x), y: hits.map(hit => hit.y),
      customdata: hits.map(hit => [bulletPartLabels[part], hit.tick]),
      marker: {{color: bulletPartColors[part], size: 13, opacity: 0.56, line: {{width: 0}}}},
      hovertemplate: "%{{customdata[0]}} hit<br>Tick %{{customdata[1]}}<extra></extra>"
    }};
  }});
  Plotly.react("bullet-heatmap-chart", traces, bulletPlotLayout, {{displayModeBar: false, responsive: true}});
}}
document.querySelectorAll(".weapon-button").forEach(button => {{
  button.addEventListener("click", () => selectHitWeapon(button.dataset.weapon));
}});
const initialHitWeapon = {json.dumps(default_hit_weapon)};
if (initialHitWeapon) selectHitWeapon(initialHitWeapon);
</script>
"""

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
    angular_velocity_by_tick[shot["tick"]] = angular_change * tick_rate / ANGULAR_LOOKBACK_TICKS

shots_with_velocity = target_shots.join(
    snapshots.select("tick", "steamid", "velocity"),
    on=["tick", "steamid"],
    how="left",
)


def calculate_weapon_metrics(weapons: list[str]) -> tuple[int, int, float, pl.DataFrame]:
    category_shots = shots_with_velocity.filter(pl.col("weapon").is_in(weapons))
    moving = category_shots.filter(pl.col("velocity") > 75)
    total = category_shots.height
    percentage = moving.height / total * 100 if total else 0.0
    return total, moving.height, percentage, moving


rifle_total, rifle_moving_count, rifle_moving_percentage, moving_shots = calculate_weapon_metrics(RIFLE_WEAPONS)
sniper_total, sniper_moving_count, sniper_moving_percentage, _ = calculate_weapon_metrics(SNIPER_WEAPONS)
smg_total, smg_moving_count, smg_moving_percentage, _ = calculate_weapon_metrics(SMG_WEAPONS)
pistol_total, pistol_moving_count, pistol_moving_percentage, _ = calculate_weapon_metrics(PISTOL_WEAPONS)
awp_unscoped_shots = target_shots.filter(
    (pl.col("weapon") == "weapon_awp") & (pl.col("scoped") == False)
).height

# Keep the names used by the existing general report fields.
total_shots_count = rifle_total
moving_shots_count = rifle_moving_count
moving_percentage = rifle_moving_percentage
velocity_75_100 = moving_shots.filter(
    (pl.col("velocity") <= 100)
).height
velocity_100_150 = moving_shots.filter(
    (pl.col("velocity") > 100) & (pl.col("velocity") <= 150)
).height
velocity_over_150 = moving_shots.filter(pl.col("velocity") > 150).height
over_150_shots = moving_shots.filter(pl.col("velocity") > 150).select("tick", "weapon")

moving_percentage = (
    moving_shots_count / total_shots_count * 100 if total_shots_count else 0.0
)

utility_deaths = demo.kills.filter(
    (pl.col("victim_name") == target_player)
    & pl.col("weapon").is_in(UTILITY_WEAPONS)
)
utility_death_ticks = utility_deaths.get_column("tick").to_list()

# Match each kill to the player's latest shot at or before the kill tick.
# Compare that shot's aim direction with the estimated direction to the victim's head.
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
fiveseven_tec9_long_kills = sum(item["distance"] > 1000 for item in fiveseven_tec9_kills)
deagle_usp_moving_total, deagle_usp_moving_count, deagle_usp_moving_percentage, _ = calculate_weapon_metrics(DEAGLE_USP)
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
    {
        "weapon": weapon,
        "count": len(values),
        "average": sum(values) / len(values),
    }
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

# Grenades contains one trajectory row per tick, so deduplicate by projectile identity.
flash_grenades = (
    demo.grenades.filter(
        (pl.col("thrower_steamid") == player_steamid)
        & (pl.col("type") == "flashbang")
    )
    .select("thrower_steamid", "entity_id", "entity_serial", "end_tick")
    .unique()
    .to_dicts()
)
player_blinds = demo.blinds.filter(pl.col("attacker_steamid") == player_steamid).to_dicts()
blind_victims_by_flash = {
    (g["entity_id"], g["entity_serial"]): [] for g in flash_grenades
}
for blind in player_blinds:
    nearest_flash = min(
        flash_grenades,
        key=lambda g: abs(blind["tick"] - g["end_tick"]),
        default=None,
    )
    if nearest_flash and abs(blind["tick"] - nearest_flash["end_tick"]) <= 2:
        blind_victims_by_flash[(nearest_flash["entity_id"], nearest_flash["entity_serial"])].append(blind)

flash_count = len(flash_grenades)
enemy_blinds = sum(
    1
    for blind in player_blinds
    if blind["attacker_side"] != blind["victim_side"]
)
teammate_blinds = sum(
    1
    for blind in player_blinds
    if blind["attacker_side"] == blind["victim_side"]
    and blind["victim_steamid"] != player_steamid
)
self_blinds = sum(1 for blind in player_blinds if blind["victim_steamid"] == player_steamid)
teammate_only_flashes = sum(
    1
    for victims in blind_victims_by_flash.values()
    if any(v["victim_steamid"] != player_steamid and v["attacker_side"] == v["victim_side"] for v in victims)
    and not any(v["attacker_side"] != v["victim_side"] for v in victims)
)
flashes_blinding_no_one = sum(not victims for victims in blind_victims_by_flash.values())
flash_teammate_or_self_count = sum(
    1
    for victims in blind_victims_by_flash.values()
    if any(
        v["victim_steamid"] == player_steamid
        or v["attacker_side"] == v["victim_side"]
        for v in victims
    )
)
flash_details = []
for grenade in flash_grenades:
    victims = blind_victims_by_flash[(grenade["entity_id"], grenade["entity_serial"])]
    enemies = sum(v["attacker_side"] != v["victim_side"] for v in victims)
    teammates = sum(
        v["attacker_side"] == v["victim_side"] and v["victim_steamid"] != player_steamid
        for v in victims
    )
    self_count = sum(v["victim_steamid"] == player_steamid for v in victims)
    if not victims:
        result = "blinded no one"
    elif not enemies and teammates:
        result = "teammates only"
    elif enemies:
        result = "enemy blinded"
    else:
        result = "self-blind only"
    flash_details.append(
        {
            "detonation_tick": grenade["end_tick"],
            "enemies": enemies,
            "teammates": teammates,
            "self": self_count,
            "result": result,
        }
    )

player_stats_frame = demo.stats.filter(pl.col("name") == target_player)
if player_stats_frame.is_empty():
    raise ValueError(f"No basic stats found for player name: {target_player}")
player_stats = player_stats_frame.row(0, named=True)
kills = player_stats["kills"] or 0
deaths = player_stats["deaths"] or 0
kd_ratio = kills / deaths if deaths else float(kills)

chart = go.Figure(
    data=[
        go.Bar(
            x=["75–100", "100–150", ">150"],
            y=[velocity_75_100, velocity_100_150, velocity_over_150],
            marker_color=["#60a5fa", "#818cf8", "#fb7185"],
            text=[velocity_75_100, velocity_100_150, velocity_over_150],
            textposition="outside",
            hovertemplate="Velocity %{x}<br>Shots: %{y}<extra></extra>",
        )
    ]
)
chart.update_layout(
    title="Moving rifle shots by velocity",
    xaxis_title="Velocity (units per second)",
    yaxis_title="Shot count",
    yaxis=dict(rangemode="tozero", dtick=1),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, Segoe UI, sans-serif", color="#1f2937"),
    margin=dict(l=50, r=24, t=60, b=55),
    height=380,
)
chart_html = chart.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False, "responsive": True})

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
html_report = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS2 Match Report — {escape(target_player)}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, Rajdhani, "Segoe UI", sans-serif; background: #0f172a; color: #f8fafc; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; padding: 38px 20px 64px; background: radial-gradient(ellipse at 50% -20%, #24364d 0, #0f172a 58%); color: #f8fafc; }}
    main {{ max-width: 1120px; margin: 0 auto; }}
    header {{ position: relative; margin: 0 0 24px; padding: 28px 30px; overflow: hidden; border: 1px solid #334155; border-radius: 18px; background: linear-gradient(115deg, #1e293b, #172235 65%, #1b2b40); box-shadow: 0 18px 50px #02061766; }}
    header::after {{ content: ""; position: absolute; right: -48px; top: -100px; width: 280px; height: 280px; border: 1px solid #64748b33; border-radius: 50%; box-shadow: 0 0 0 28px #64748b0d, 0 0 0 58px #64748b0a; }}
    .eyebrow {{ margin: 0 0 9px; color: #38bdf8; font-size: .72rem; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(1.8rem, 4vw, 2.7rem); letter-spacing: -.045em; }}
    .header-meta {{ display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 12px; color: #94a3b8; font-size: .95rem; }}
    .header-meta strong {{ color: #e2e8f0; font-weight: 650; }}
    section, details {{ margin: 18px 0; padding: 24px; border: 1px solid #334155; border-radius: 16px; background: #1e293b; box-shadow: 0 12px 32px #02061733; }}
    h2 {{ margin: 0 0 18px; font-size: 1.13rem; letter-spacing: .02em; }}
    h3 {{ margin: 22px 0 12px; color: #e2e8f0; font-size: 1rem; }}
    .subtitle {{ color: #94a3b8; margin: 0 0 8px; }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .stat-card {{ display: flex; min-height: 104px; flex-direction: column; justify-content: space-between; gap: 9px; padding: 17px 18px; border: 1px solid #334155; border-radius: 12px; background: linear-gradient(145deg, #263449, #1b283a); }}
    .stat-label {{ color: #94a3b8; font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }}
    .stat-card strong {{ color: #f8fafc; font-size: 1.65rem; line-height: 1; font-variant-numeric: tabular-nums; }}
    .stat-card:first-child strong {{ color: #4ade80; }}
    .conclusion {{ margin: 10px 0; padding: 14px 16px; border: 1px solid transparent; border-left-width: 4px; border-radius: 10px; line-height: 1.55; }}
    .warning-red {{ background: #7f1d1d33; border-color: #ef444466; border-left-color: #ef4444; color: #fecaca; }}
    .warning-yellow {{ background: #713f1233; border-color: #f59e0b55; border-left-color: #fbbf24; color: #fde68a; }}
    .warning-orange {{ background: #7c2d1233; border-color: #f9731655; border-left-color: #fb923c; color: #fed7aa; }}
    .note-gentle {{ background: #14532d33; border-color: #22c55e55; border-left-color: #4ade80; color: #bbf7d0; }}
    .hint-gray {{ background: #33415566; border-color: #64748b55; border-left-color: #94a3b8; color: #cbd5e1; }}
    .diagnosis-list {{ display: grid; gap: 8px; }}
    .visual-grid {{ display: grid; grid-template-columns: minmax(280px, .9fr) minmax(0, 1.1fr); gap: 22px; align-items: start; }}
    .visual-panel {{ min-width: 0; padding: 18px; border: 1px solid #334155; border-radius: 13px; background: #172235; }}
    .visual-panel h3 {{ margin: 0 0 14px; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    th, td {{ padding: 11px 12px; border-bottom: 1px solid #334155; }}
    th {{ color: #94a3b8; font-size: .76rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; }}
    td {{ color: #e2e8f0; }} tbody tr:hover {{ background: #ffffff08; }}
    .table-wrap {{ overflow-x: auto; }}
    .weapon-button {{ border: 1px solid #475569; border-radius: 999px; padding: 8px 14px; background: #172235; color: #cbd5e1; cursor: pointer; font: inherit; transition: border-color .15s, background .15s, color .15s; }}
    .weapon-button:hover {{ border-color: #38bdf8; color: #f8fafc; }}
    .weapon-button.active {{ background: #075985; color: white; border-color: #0ea5e9; box-shadow: 0 0 18px #0ea5e933; }}
    .hit-model-widget {{ margin: 0; padding: 0; border: 0; background: transparent; }}
    .weapon-buttons {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 7px; margin-bottom: 12px; }}
    .bullet-heatmap-stage {{ width: min(350px, 100%); margin: 0 auto; padding: 0; aspect-ratio: 2 / 3; overflow: hidden; background: transparent; }}
    .bullet-heatmap-stage > div {{ width: 100% !important; height: 100% !important; }}
    #bullet-heatmap-chart, #bullet-heatmap-chart .js-plotly-plot, #bullet-heatmap-chart .plot-container {{ width: 100% !important; height: 100% !important; }}
    .bullet-heatmap-legend {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; margin: 5px 0 12px; color: #94a3b8; font-size: .82rem; }}
    .bullet-heatmap-legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
    .dot {{ width: 10px; height: 10px; display: inline-block; border-radius: 50%; opacity: .9; }}
    .head-dot {{ background: #ef4444; }} .torso-dot {{ background: #f97316; }} .limb-dot {{ background: #3b82f6; }}
    details {{ padding: 0; overflow: hidden; }} details > summary {{ cursor: pointer; padding: 19px 22px; color: #e2e8f0; font-weight: 750; list-style-position: inside; }}
    details[open] > summary {{ border-bottom: 1px solid #334155; background: #223147; }}
    .details-content {{ padding: 8px 20px 20px; }} .details-content section {{ margin: 16px 0; padding: 20px; background: #172235; box-shadow: none; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin: 0; }}
    .summary div {{ padding: 13px; border: 1px solid #334155; border-radius: 10px; background: #1e293b; }}
    .summary dt {{ color: #94a3b8; font-size: .8rem; margin-bottom: 6px; }} .summary dd {{ margin: 0; color: #f8fafc; font-weight: 700; font-size: 1.1rem; }}
    .chart {{ width: 100%; }}
    @media (max-width: 760px) {{ body {{ padding: 20px 12px 44px; }} section {{ padding: 18px; }} .visual-grid {{ grid-template-columns: 1fr; }} .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} header {{ padding: 23px 20px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Tactical performance review</p>
      <h1>CS2 Match Report</h1>
      <p class="header-meta">Player <strong>{escape(target_player)}</strong> &nbsp; · &nbsp; Map <strong>{escape(str(map_name))}</strong></p>
    </header>
    <section>
      <h2>Match Stats</h2>
      <div class="stats">{stats_cards}</div>
    </section>
    <section>
      <h2>Match Diagnosis</h2>
      {diagnosis_html if diagnosis_html else '<p class="subtitle">No playstyle threshold was triggered for this match.</p>'}
    </section>
    <section>
      <h2>Weapon Visuals</h2>
      <div class="visual-grid">
        <div class="visual-panel"><h3>Where are you actually hitting?</h3>{hit_model_html}</div>
        <div class="visual-panel">
          <h3>Weapon Playstyle Breakdown</h3>
          <div class="table-wrap"><table><thead><tr><th>Category</th><th>Total shots</th><th>Moving shots</th><th>Moving %</th></tr></thead><tbody>{weapon_playstyle_rows}</tbody></table></div>
          <h3>Pistol Engagements</h3>
          <p class="subtitle">Average kill distance: {f'{average_pistol_kill_distance:.1f} units' if average_pistol_kill_distance is not None else 'N/A'}.</p>
          <p class="subtitle">Distance buckets — close (&lt;500): {pistol_distance_buckets['close']}; medium (500–1000): {pistol_distance_buckets['medium']}; long (&gt;1000): {pistol_distance_buckets['long']}.</p>
          <p class="subtitle">Five-SeveN/Tec-9 average: {f'{average_fiveseven_tec9_distance:.1f} units' if average_fiveseven_tec9_distance is not None else 'N/A'}; long-range kills: {fiveseven_tec9_long_kills}.</p>
        </div>
      </div>
    </section>
    <details>
      <summary>View detailed data</summary>
      <div class="details-content">
    <section>
      <div class="chart">{chart_html}</div>
    </section>
    <section>
      <h2>Moving-shot summary</h2>
      <dl class="summary">
        <div><dt>Rifle total shots</dt><dd>{total_shots_count}</dd></div>
        <div><dt>Moving rifle shots</dt><dd>{moving_shots_count}</dd></div>
        <div><dt>Moving-shot percentage</dt><dd>{moving_percentage:.1f}%</dd></div>
        <div><dt>Deaths holding utility</dt><dd>{utility_deaths.height}</dd></div>
      </dl>
    </section>
    <section>
      <h2>Weapon Playstyle Breakdown</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>Category</th><th>Total shots</th><th>Moving shots</th><th>Moving-shot percentage</th></tr></thead>
        <tbody>{weapon_playstyle_rows}</tbody>
      </table></div>
      <p>Average pistol kill distance: {f'{average_pistol_kill_distance:.1f} units' if average_pistol_kill_distance is not None else 'N/A'}.</p>
      <p>Pistol kill distances: close (&lt;500): {pistol_distance_buckets['close']}; medium (500–1000): {pistol_distance_buckets['medium']}; long (&gt;1000): {pistol_distance_buckets['long']}.</p>
      <p>Five-SeveN/Tec-9 average kill distance: {f'{average_fiveseven_tec9_distance:.1f} units' if average_fiveseven_tec9_distance is not None else 'N/A'}; long-range kills: {fiveseven_tec9_long_kills}.</p>
    </section>
    <section>
      <h2>Aim deviation on kills</h2>
      <p>Average deviation: <strong>{average_deviation_html}</strong></p>
      <p>AK Avg Pitch Bias: <strong>{f'{ak_avg_pitch_bias:.2f} deg' if ak_avg_pitch_bias is not None else 'N/A'}</strong></p>
      <p class="subtitle">Estimated from firing direction to victim head position (victim z + 64).</p>
      <h3>By weapon</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>Weapon</th><th>Average deviation</th><th>Sample count</th></tr></thead>
        <tbody>{weapon_deviation_rows}</tbody>
      </table></div>
      <h3>Kills above 10 degrees</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>Kill tick</th><th>Victim</th><th>Deviation</th><th>Firing pitch</th><th>Firing yaw</th><th>Victim pitch</th><th>Victim yaw</th></tr></thead>
        <tbody>{high_deviation_rows}</tbody>
      </table></div>
      <h3>Per-kill detail</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>Kill tick</th><th>Shot tick</th><th>Victim</th><th>Weapon</th><th>Deviation</th></tr></thead>
        <tbody>{kill_deviation_rows}</tbody>
      </table></div>
    </section>
    <section>
      <h2>Suspected firing before crosshair settles</h2>
      <p class="subtitle">Angular deviation is the pitch/yaw change from the snapshot {ANGULAR_LOOKBACK_TICKS} ticks before firing to the firing angle.</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Shot tick</th><th>Weapon</th><th>Angular velocity</th><th>Angular deviation</th><th>Hit enemy?</th></tr></thead>
        <tbody>{suspected_fire_rows}</tbody>
      </table></div>
    </section>
    <section>
      <h2>Flashbang summary</h2>
      <p>{flash_count} flashbangs thrown; {enemy_blinds} enemy blinds; {teammate_blinds} teammate blinds; {self_blinds} self-blinds; {flashes_blinding_no_one} flashes blinded no one.</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Detonation tick</th><th>Enemies blinded</th><th>Teammates blinded</th><th>Self-blinds</th><th>Result</th></tr></thead>
        <tbody>{flash_detail_rows}</tbody>
      </table></div>
    </section>
      </div>
    </details>
  </main>
</body>
</html>
"""

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
