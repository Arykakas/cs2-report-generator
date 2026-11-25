"""HTML template rendering for the match report."""

from html import escape

from ..localization import translate

_DIAGNOSIS_LABEL_KEYS = {
  "warning-red": "diagnosis.label.priority",
  "warning-yellow": "diagnosis.label.review",
  "warning-orange": "diagnosis.label.range",
  "note-gentle": "diagnosis.label.playstyle",
  "hint-gray": "diagnosis.label.signal",
}


def render_diagnosis_cards(messages: list[tuple], locale: str = "en") -> str:
    """Render diagnosis messages as consistent, severity-coded cards."""
    cards = []
    for index, item in enumerate(messages, start=1):
        kind, message = item[:2]
        anchor = item[2] if len(item) > 2 else None
        label = translate(locale, _DIAGNOSIS_LABEL_KEYS.get(kind, "diagnosis.label.note"))
        tag = "a" if anchor else "article"
        link_attrs = f' href="#{escape(anchor, quote=True)}"' if anchor else ""
        link_class = " diagnosis-card-link" if anchor else ""
        cards.append(
            f'<{tag} class="diagnosis-card{link_class} {kind}"{link_attrs}>'
            f'<div class="diagnosis-card-head">'
            f'<span class="diagnosis-card-label">{escape(label)}</span>'
            f'<span class="diagnosis-card-index">{escape(translate(locale, "diagnosis.card_index", index=index))}</span>'
            f'</div><div class="diagnosis-card-rule"></div>'
            f'<p class="diagnosis-copy">{escape(message)}</p>'
            f'<div class="diagnosis-card-footer">{escape(translate(locale, "diagnosis.intelligence"))}</div>'
            f'</{tag}>'
        )
    return "".join(cards)


_TEMPLATE = r'''

f"""<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(translate(locale, "report.title"))} — {escape(target_player)}</title>
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
    .diagnosis-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 260px)); justify-content: start; align-items: stretch; gap: 14px; }}
    .diagnosis-card {{ position: relative; isolation: isolate; display: flex; flex-direction: column; width: 100%; min-height: 340px; margin: 0; padding: 18px; overflow: hidden; border: 1px solid #334155; border-top: 2px solid var(--diagnosis-accent); border-radius: 14px; background: linear-gradient(155deg, #1b2738, #172235 72%); color: #e2e8f0; box-shadow: inset 0 1px #ffffff0a, 0 10px 26px #02061733; }}
    .diagnosis-card-link {{ color: inherit; text-decoration: none; cursor: pointer; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }}
    .diagnosis-card-link:hover, .diagnosis-card-link:focus-visible {{ transform: translateY(-3px); border-color: var(--diagnosis-accent); box-shadow: inset 0 1px #ffffff0a, 0 14px 30px #02061766; outline: none; }}
    html {{ scroll-behavior: smooth; scroll-padding-top: 24px; }}
    .diagnosis-card::after {{ content: ""; position: absolute; z-index: -1; right: -48px; bottom: -52px; width: 112px; height: 112px; border: 1px solid #ffffff12; border-radius: 50%; box-shadow: 0 0 0 14px #ffffff05, 0 0 0 29px #ffffff03; pointer-events: none; }}
    .diagnosis-card-head {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .diagnosis-card-label {{ color: var(--diagnosis-accent); font: 700 .67rem 'Fira Code', monospace; letter-spacing: .1em; text-transform: uppercase; }}
    .diagnosis-card-index {{ color: #64748b; font: 500 .62rem 'Fira Code', monospace; letter-spacing: .04em; white-space: nowrap; }}
    .diagnosis-card-rule {{ width: 100%; height: 1px; margin: 14px 0 17px; background: linear-gradient(90deg, #47556999, transparent); }}
    .diagnosis-copy {{ margin: 0; color: #e2e8f0; font-size: .96rem; line-height: 1.65; }}
    .diagnosis-card-footer {{ margin-top: auto; padding-top: 18px; color: #64748b; font: 500 .58rem 'Fira Code', monospace; letter-spacing: .12em; }}
    .warning-red {{ --diagnosis-accent: #f87171; }}
    .warning-yellow {{ --diagnosis-accent: #fbbf24; }}
    .warning-orange {{ --diagnosis-accent: #fb923c; }}
    .note-gentle {{ --diagnosis-accent: #4ade80; }}
    .hint-gray {{ --diagnosis-accent: #94a3b8; }}
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
    @media (max-width: 540px) {{ .diagnosis-grid {{ grid-template-columns: minmax(0, 1fr); }} .diagnosis-card {{ min-height: 270px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">{escape(translate(locale, "report.v1.eyebrow"))}</p>
      <h1>{escape(translate(locale, "report.title"))}</h1>
      <p class="header-meta">{escape(translate(locale, "report.v2.player"))} <strong>{escape(target_player)}</strong> &nbsp; · &nbsp; {escape(translate(locale, "report.v2.map"))} <strong>{escape(str(map_name))}</strong></p>
    </header>
    <section>
      <h2>{escape(translate(locale, "report.v1.match_stats"))}</h2>
      <div class="stats">{stats_cards}</div>
    </section>
    <section>
      <h2>{escape(translate(locale, "report.v1.match_diagnosis"))}</h2>
      <div style="display: flex; flex-direction: column; gap: 12px; width: 100%;">{(diagnosis_html if diagnosis_html else f'<p class="subtitle">{escape(translate(locale, "diagnosis.no_obvious_errors"))}</p>')}</div>
    </section>
    <section id="weapon-visuals">
      <h2>{escape(translate(locale, "report.v1.weapon_visuals"))}</h2>
      <div class="visual-grid">
        <div class="visual-panel"><h3>{escape(translate(locale, "report.v1.where_hits"))}</h3>{hit_model_html}</div>
        <div class="visual-panel">
          <h3>{escape(translate(locale, "report.v1.weapon_playstyle"))}</h3>
          <div class="table-wrap"><table><thead><tr><th>{escape(translate(locale, "report.v1.category"))}</th><th>{escape(translate(locale, "report.v1.total_shots"))}</th><th>{escape(translate(locale, "report.v1.moving_shots"))}</th><th>{escape(translate(locale, "report.v1.moving_percent"))}</th></tr></thead><tbody>{weapon_playstyle_rows}</tbody></table></div>
          <h3>{escape(translate(locale, "report.v1.pistol_engagements"))}</h3>
          <p class="subtitle">{escape(translate(locale, "report.v1.average_kill_distance", distance=(f'{average_pistol_kill_distance:.1f} {translate(locale, "unit.game_units")}' if average_pistol_kill_distance is not None else 'N/A')))}</p>
          <p class="subtitle">{escape(translate(locale, "report.v1.distance_buckets", close=pistol_distance_buckets['close'], medium=pistol_distance_buckets['medium'], long=pistol_distance_buckets['long']))}</p>
          <p class="subtitle">{escape(translate(locale, "report.v1.fiveseven_average", distance=(f'{average_fiveseven_tec9_distance:.1f} {translate(locale, "unit.game_units")}' if average_fiveseven_tec9_distance is not None else 'N/A'), kills=fiveseven_tec9_long_kills))}</p>
        </div>
      </div>
    </section>
    <details>
      <summary>{escape(translate(locale, "report.v1.details"))}</summary>
      <div class="details-content">
    <section>
      <div class="chart">{chart_html}</div>
    </section>
    <section>
      <h2>{escape(translate(locale, "report.v1.aim_deviation"))}</h2>
      <p>{escape(translate(locale, "report.v2.average_deviation", deviation=average_deviation_html))}</p>
      <h3>{escape(translate(locale, "report.v1.by_weapon"))}</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>{escape(translate(locale, "report.v1.weapon"))}</th><th>{escape(translate(locale, "report.v1.average_deviation"))}</th><th>{escape(translate(locale, "report.v1.sample_count"))}</th></tr></thead>
        <tbody>{weapon_deviation_rows}</tbody>
      </table></div>
    </section>
    {suspected_fire_section_html}
    <section id="flashbang-table">
      <h2>{escape(translate(locale, "report.v1.flash_summary"))}</h2>
      <p>{escape(translate(locale, "report.v1.flash_overview", throws=flash_count, enemies=enemy_blinds, teammates=teammate_blinds, self_blinds=self_blinds, no_one=flashes_blinding_no_one))}</p>
      <div class="table-wrap"><table>
        <thead><tr><th>{escape(translate(locale, "report.v2.flash_enemies"))}</th><th>{escape(translate(locale, "report.v2.flash_teammates"))}</th><th>{escape(translate(locale, "report.v2.flash_self"))}</th><th>{escape(translate(locale, "report.v2.flash_outcome"))}</th></tr></thead>
        <tbody>{flash_detail_rows}</tbody>
      </table></div>
    </section>
      </div>
    </details>
  </main>
  <script>
    document.querySelectorAll('.diagnosis-card-link').forEach(card => {{
      card.addEventListener('click', event => {{
        event.preventDefault();
        const targetId = card.getAttribute('href')?.slice(1);
        const target = targetId ? document.getElementById(targetId) : null;
        if (!target) return;
        const details = target.closest('details');
        if (details) details.open = true;
        requestAnimationFrame(() => target.scrollIntoView({{ behavior: 'smooth', block: 'start' }}));
      }});
    }});
  </script>
</body>
</html>
"""
'''

def render_html_report(context: dict) -> str:
    """Render the report using the prepared analysis context."""
    return eval(
        _TEMPLATE,
        {"escape": escape, "translate": translate, "locale": context.get("locale", "en")},
        context,
    )


