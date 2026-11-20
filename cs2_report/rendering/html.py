"""HTML template rendering for the match report."""

from html import escape

_TEMPLATE = r'''

f"""<!doctype html>
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
    .impact-dot {{ background: #9ca3af; }}
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
      {(diagnosis_html if diagnosis_html else '<p class="subtitle">No playstyle threshold was triggered for this match.</p>')}
    </section>
    <section>
      <h2>Weapon Visuals</h2>
      <div class="visual-grid">
        <div class="visual-panel"><h3>Where are you actually hitting?</h3>{hit_model_html}</div>
        <div class="visual-panel">
          <h3>Weapon Playstyle Breakdown</h3>
          <div class="table-wrap"><table><thead><tr><th>Category</th><th>Total shots</th><th>Moving shots</th><th>Moving %</th></tr></thead><tbody>{weapon_playstyle_rows}</tbody></table></div>
          <h3>Pistol Engagements</h3>
          <p class="subtitle">Average kill distance: {(f'{average_pistol_kill_distance:.1f} units' if average_pistol_kill_distance is not None else 'N/A')}.</p>
          <p class="subtitle">Distance buckets — close (&lt;500): {pistol_distance_buckets['close']}; medium (500–1000): {pistol_distance_buckets['medium']}; long (&gt;1000): {pistol_distance_buckets['long']}.</p>
          <p class="subtitle">Five-SeveN/Tec-9 average: {(f'{average_fiveseven_tec9_distance:.1f} units' if average_fiveseven_tec9_distance is not None else 'N/A')}; long-range kills: {fiveseven_tec9_long_kills}.</p>
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
      <p>Average pistol kill distance: {(f'{average_pistol_kill_distance:.1f} units' if average_pistol_kill_distance is not None else 'N/A')}.</p>
      <p>Pistol kill distances: close (&lt;500): {pistol_distance_buckets['close']}; medium (500–1000): {pistol_distance_buckets['medium']}; long (&gt;1000): {pistol_distance_buckets['long']}.</p>
      <p>Five-SeveN/Tec-9 average kill distance: {(f'{average_fiveseven_tec9_distance:.1f} units' if average_fiveseven_tec9_distance is not None else 'N/A')}; long-range kills: {fiveseven_tec9_long_kills}.</p>
    </section>
    <section>
      <h2>Aim deviation on kills</h2>
      <p>Average deviation: <strong>{average_deviation_html}</strong></p>
      <p>AK Avg Pitch Bias: <strong>{(f'{ak_avg_pitch_bias:.2f} deg' if ak_avg_pitch_bias is not None else 'N/A')}</strong></p>
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
'''

def render_html_report(context: dict) -> str:
    """Render the report using the prepared analysis context."""
    return eval(_TEMPLATE, {"escape": escape}, context)
