"""Hitgroup analysis and the interactive bullet-hole heatmap."""

from base64 import b64encode
from html import escape
import json
import math
from pathlib import Path
import random

import polars as pl
import plotly.graph_objects as go

from ..constants import BODY_ANCHORS, BODY_PARTS, HITGROUP_BY_ID, WEAPON_CATEGORIES, WEAPON_LABELS


def _polygon_path(points: list[tuple[float, float]]) -> str:
    commands = [
        f"{'M' if index == 0 else 'L'} {x:.1f},{y:.1f}"
        for index, (x, y) in enumerate(points)
    ]
    return " ".join(commands) + " Z"


def _bullet_hole_data_uri() -> str:
    outer_points = []
    inner_points = []
    for index in range(32):
        angle = (2 * math.pi * index) / 32
        radius = 53 + 3.2 * math.sin(index * 2.7) + 2.0 * math.cos(index * 4.1)
        outer_points.append((64 + radius * math.cos(angle), 64 + radius * math.sin(angle)))
    for index in range(28):
        angle = (2 * math.pi * index) / 28
        radius = 43 + 2.2 * math.sin(index * 2.3) + 1.4 * math.cos(index * 3.7)
        inner_points.append((64 + radius * math.cos(angle), 64 + radius * math.sin(angle)))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
<defs>
  <radialGradient id="impact" cx="46%" cy="40%" r="64%">
    <stop offset="0%" stop-color="#05070a"/>
    <stop offset="42%" stop-color="#111820"/>
    <stop offset="58%" stop-color="#343b43"/>
    <stop offset="72%" stop-color="#d6d9dc"/>
    <stop offset="82%" stop-color="#737b84"/>
    <stop offset="100%" stop-color="#222a34"/>
  </radialGradient>
  <radialGradient id="tint" cx="50%" cy="50%" r="50%">
    <stop offset="52%" stop-color="#9ca3af" stop-opacity="0"/>
    <stop offset="83%" stop-color="#9ca3af" stop-opacity=".12"/>
    <stop offset="100%" stop-color="#9ca3af" stop-opacity=".62"/>
  </radialGradient>
  <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="2.2"/>
    <feOffset dy="1.5"/>
    <feComponentTransfer><feFuncA type="linear" slope=".55"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<path d="{_polygon_path(outer_points)}" fill="#1b222b" stroke="#737b84" stroke-width="2.3" filter="url(#shadow)"/>
<path d="{_polygon_path(inner_points)}" fill="url(#impact)" stroke="#e2e6e9" stroke-opacity=".78" stroke-width="2.3"/>
<circle cx="64" cy="64" r="25" fill="#080b0f" stroke="#434a52" stroke-width="3"/>
<circle cx="64" cy="64" r="17" fill="#030508"/>
<path d="M 64 17 L 67 26 M 100 32 L 91 39 M 111 65 L 101 64 M 94 99 L 87 90 M 61 111 L 62 101 M 29 93 L 38 87 M 17 60 L 27 61 M 35 29 L 42 38" stroke="#f1f5f9" stroke-opacity=".72" stroke-width="2.4" stroke-linecap="round"/>
<path d="M 64 13 L 64 24 M 115 64 L 104 64 M 64 115 L 64 104 M 13 64 L 24 64" stroke="#9ca3af" stroke-opacity=".72" stroke-width="2" stroke-linecap="round"/>
</svg>'''
    return "data:image/svg+xml;base64," + b64encode(svg.encode("utf-8")).decode("ascii")


def analyze_hits(demo, player_steamid: int) -> dict:
    """Build per-weapon hit distribution and the interactive hit-map HTML."""
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

    bullet_hole_texture = _bullet_hole_data_uri()
    bullet_points_by_weapon = {}
    for hit_index, hit in enumerate(player_hits.to_dicts()):
        raw_weapon = str(hit.get("weapon") or "").removeprefix("weapon_")
        body_part = HITGROUP_BY_ID.get(hit.get("hitgroup"))
        if raw_weapon not in hit_model_data or body_part is None:
            continue
        center_x, center_y, spread_x, spread_y = BODY_ANCHORS[body_part]
        rng = random.Random(
            f"{hit.get('tick')}:{hit.get('attacker_steamid')}:{hit.get('victim_steamid')}:{raw_weapon}:{hit_index}"
        )
        bullet_points_by_weapon.setdefault(raw_weapon, []).append(
            {
                "part": body_part,
                "x": round(center_x + rng.uniform(-spread_x, spread_x), 1),
                "y": round(center_y + rng.uniform(-spread_y, spread_y), 1),
                "tick": hit.get("tick"),
            }
        )

    bullet_points_json = json.dumps(
        bullet_points_by_weapon, separators=(",", ":"), ensure_ascii=True
    )
    human_svg_path = Path(__file__).resolve().parents[2] / "human_model.svg"
    human_svg = human_svg_path.read_text(encoding="utf-8").replace(
        'fill="#000000"', 'fill="#d1d5db"'
    )
    human_svg_uri = "data:image/svg+xml;base64," + b64encode(
        human_svg.encode("utf-8")
    ).decode("ascii")

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
  <div class="bullet-heatmap-legend"><span><i class="dot impact-dot"></i>Bullet impact</span></div>
  <p class="subtitle">Each impact mark is one hit. Placement is approximated by hitgroup; hover a mark to see its tick.</p>
</div>
<script>
const bulletPointsByWeapon = {bullet_points_json};
const bulletHoleTexture = {json.dumps(bullet_hole_texture)};
const bulletPartOrder = ["head", "chest", "stomach", "left_arm", "right_arm", "left_leg", "right_leg"];
const bulletPartLabels = {{"head": "Head", "chest": "Chest", "stomach": "Stomach", "left_arm": "Left arm", "right_arm": "Right arm", "left_leg": "Left leg", "right_leg": "Right leg"}};
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
  const impactImages = points.map(hit => ({{
    source: bulletHoleTexture,
    xref: "x", yref: "y", x: hit.x, y: hit.y,
    sizex: 40.4, sizey: 40.4, xanchor: "center", yanchor: "middle",
    sizing: "stretch", opacity: 1, layer: "above", captureevents: false
  }}));
  const layoutForWeapon = {{...bulletPlotLayout, images: [bulletPlotLayout.images[0], ...impactImages]}};
  const traces = bulletPartOrder.map(part => {{
    const hits = points.filter(hit => hit.part === part);
    return {{
      type: "scatter", mode: "markers", name: bulletPartLabels[part],
      x: hits.map(hit => hit.x), y: hits.map(hit => hit.y),
      customdata: hits.map(hit => [bulletPartLabels[part], hit.tick]),
      marker: {{color: "rgba(0, 0, 0, 0.001)", size: 11, opacity: 0.01, line: {{width: 0}}}},
      hovertemplate: "%{{customdata[0]}} hit<br>Tick %{{customdata[1]}}<extra></extra>"
    }};
  }});
  Plotly.react("bullet-heatmap-chart", traces, layoutForWeapon, {{displayModeBar: false, responsive: true}});
}}
document.querySelectorAll(".weapon-button").forEach(button => {{
  button.addEventListener("click", () => selectHitWeapon(button.dataset.weapon));
}});
const initialHitWeapon = {json.dumps(default_hit_weapon)};
if (initialHitWeapon) selectHitWeapon(initialHitWeapon);
</script>
"""
    return {"hit_model_data": hit_model_data, "hit_model_html": hit_model_html}
