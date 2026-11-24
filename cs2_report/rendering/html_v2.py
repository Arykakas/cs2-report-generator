"""Standalone HTML renderer for the coaching-focused Report 2.0."""

from html import escape


def render_html_report_v2(context: dict) -> str:
    """Render Report 2.0 without routing through the legacy report template."""
    player = escape(str(context["target_player"]))
    map_name = escape(str(context["map_name"]))
    archetype = context["archetype_analysis"]
    scores = archetype["scores"]
    score_labels = (
        ("Aggression", "aggression", scores.get("aggression", 0), "#fb7185"),
        ("Precision", "precision", scores.get("precision", 0), "#38bdf8"),
        ("Utility", "utility", scores.get("utility", 0), "#34d399"),
        ("Positioning", "positioning", scores.get("positioning", 0), "#a78bfa"),
    )
    tied_distinctions = archetype.get("tied_distinctions", [])
    distinction_html = ""
    if tied_distinctions:
        distinction_html = (
            '<div class="focus-row"><span class="focus-chip">Tied distinctions: '
            f'<strong>{escape(" + ".join(tied_distinctions))}</strong></span></div>'
        )

    score_cards = ""
    for label, trait_key, value, color in score_labels:
        is_max = "is-max" if scores.get(f"{trait_key}_is_max") else ""
        score_cards += (
            f'<article class="score-card {is_max}" style="--score-color:{color}">\n'
            f'  <span class="label">{escape(label)}</span>\n'
            f'  <strong class="value">{float(value):.0f}</strong>\n'
            f'  <div class="score-track"><i style="width:{max(0, min(100, float(value))):.1f}%"></i></div>\n'
            f'</article>\n'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS2 Report 2.0 — {player}</title>
  <style>
    :root {{ color-scheme: normal; font-family: Inter, "Segoe UI", sans-serif; color: #eef2ff; background: transparent; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; scroll-padding-top: 24px; }}
    body {{ margin: 0; padding: 34px 18px 60px; background: transparent; }}
    main {{ width: min(1180px, 100%); margin: 0 auto; }}
    header, section, details {{ border: 1px solid #334155; border-radius: 16px; background: #172235; box-shadow: 0 14px 36px #02061744; }}
    header {{ padding: 28px; margin-bottom: 18px; background: linear-gradient(120deg, #1c2a42, #18223a 65%, #251d42); }}
    .eyebrow {{ color: #a78bfa; font-size: .73rem; font-weight: 800; letter-spacing: .17em; text-transform: uppercase; }}
    h1 {{ margin: 6px 0 8px; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.045em; }}
    .meta, .muted {{ color: #9aa9bf; }}
    section {{ margin: 18px 0; padding: 22px; }}
    h2 {{ margin: 0 0 16px; font-size: 1.15rem; }}
    h3 {{ margin: 0 0 12px; font-size: 1rem; }}
    .archetype {{ position: relative; overflow: hidden; border-color: #6751a5; background: linear-gradient(120deg, #211c3b, #172235 72%); }}
    .archetype::after {{ content: ""; position: absolute; right: -85px; top: -110px; width: 290px; height: 290px; border: 1px solid #a78bfa22; border-radius: 50%; box-shadow: 0 0 0 28px #a78bfa08, 0 0 0 58px #a78bfa05; pointer-events: none; }}
    .archetype-name {{ margin: 0 0 12px; color: #c4b5fd; font-size: clamp(1.6rem, 4vw, 2.3rem); font-weight: 800; }}
    .archetype-summary {{ max-width: 850px; margin: 0; color: #dbe5f5; font-size: 1.02rem; line-height: 1.7; }}
    .focus-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
    .focus-chip {{ padding: 9px 12px; border: 1px solid #475569; border-radius: 10px; background: #111a2d; color: #cbd5e1; font-size: .88rem; }}
    .scores {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .score-card {{ padding: 15px; border: 1px solid #334155; border-radius: 12px; background: #111a2d; transition: transform 0.2s, box-shadow 0.2s; }}\
    .score-card.is-max {{ border: 2px solid #ffd700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.3); transform: scale(1.02); }}\
    .score-card span {{ color: #9aa9bf; font-size: .76rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }}\
    .score-card strong {{ display: block; margin: 9px 0; color: var(--score-color); font-size: 1.8rem; }}\
    .score-track {{ height: 6px; overflow: hidden; border-radius: 8px; background: #334155; }}\
    .score-track i {{ display: block; height: 100%; background: var(--score-color); }}\
    .score-card:hover {{ transform: scale(1.05); }}\
    .score-card:hover .score-track i {{ filter: brightness(1.2); }}\
    .score-card:hover {{ z-index: 10; }}\
    .score-card:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}\
    .score-card:hover {{ background: #1e293b; }}\
    .score-card:hover {{ border-color: #475569; }}\

    .score-card {{ padding: 15px; border: 1px solid #334155; border-radius: 12px; background: #111a2d; }}
    .score-card span {{ color: #9aa9bf; font-size: .76rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }}
    .score-card strong {{ display: block; margin: 9px 0; color: var(--score-color); font-size: 1.8rem; }}
    .score-track {{ height: 6px; overflow: hidden; border-radius: 8px; background: #29364b; }}
    .score-track i {{ display: block; height: 100%; border-radius: inherit; background: var(--score-color); }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
    .stat-card {{ min-height: 95px; padding: 15px; border: 1px solid #334155; border-radius: 11px; background: #111a2d; }}
    .stat-label {{ display: block; margin-bottom: 10px; color: #9aa9bf; font-size: .76rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }}
    .stat-card strong {{ font-size: 1.55rem; }}
    .columns {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; align-items: start; }}
    .panel {{ min-width: 0; padding: 17px; border: 1px solid #334155; border-radius: 12px; background: #111a2d; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #2c3a51; }}
    th {{ color: #9aa9bf; font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; }}
    td {{ color: #dbe5f5; }}
    .diagnosis-grid {{ display: flex; flex-wrap: wrap; align-items: stretch; gap: 12px; }}
    .diagnosis-card {{ display: flex; flex: 0 1 250px; flex-direction: column; min-height: 205px; padding: 15px; border: 1px solid #3b4960; border-top: 2px solid var(--diagnosis-accent, #a78bfa); border-radius: 12px; background: #111a2d; color: #e2e8f0; text-decoration: none; }}
    .diagnosis-card-link {{ cursor: pointer; }}
    .diagnosis-card-link:hover {{ border-color: var(--diagnosis-accent, #a78bfa); }}
    .diagnosis-card-head {{ display: flex; justify-content: space-between; gap: 8px; color: var(--diagnosis-accent, #a78bfa); font-size: .72rem; text-transform: uppercase; }}
    .diagnosis-card-rule {{ height: 1px; margin: 12px 0; background: #394961; }}
    .diagnosis-copy {{ line-height: 1.55; }}
    .diagnosis-card-footer {{ margin-top: auto; padding-top: 12px; color: #74849d; font-size: .62rem; letter-spacing: .1em; }}
    details {{ margin: 18px 0; overflow: hidden; }}
    details > summary {{ padding: 17px 20px; cursor: pointer; font-weight: 750; }}
    .details-content {{ padding: 0 20px 18px; }}
    .details-content section {{ padding: 18px; background: #111a2d; box-shadow: none; }}
    .weapon-buttons {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 7px; margin-bottom: 12px; }}
    .weapon-button {{ padding: 8px 12px; border: 1px solid #475569; border-radius: 999px; background: #172235; color: #cbd5e1; cursor: pointer; }}
    .weapon-button.active {{ background: #075985; border-color: #0ea5e9; color: white; }}
    .bullet-heatmap-stage {{ width: min(350px, 100%); margin: 0 auto; aspect-ratio: 2 / 3; overflow: hidden; }}
    .bullet-heatmap-stage > div, #bullet-heatmap-chart, #bullet-heatmap-chart .js-plotly-plot, #bullet-heatmap-chart .plot-container {{ width: 100% !important; height: 100% !important; }}
    .subtitle {{ color: #9aa9bf; }}
    .chart {{ width: 100%; }}
    @media (max-width: 780px) {{ .columns {{ grid-template-columns: 1fr; }} .scores {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">Report 2.0 / Coaching summary</div>
      <h1>CS2 Match Review</h1>
      <div class="meta">Player <strong>{player}</strong> &nbsp;·&nbsp; Map <strong>{map_name}</strong></div>
    </header>
    <section class="archetype">
      <div class="eyebrow">Your player archetype</div>
      <h2 class="archetype-name">{escape(str(archetype["archetype"]))}</h2>
      <p class="archetype-summary">{escape(str(archetype["summary"]))}</p>
      <div class="focus-row">
        <span class="focus-chip">Primary strength: <strong>{escape(str(archetype["primary_trait"]))}</strong></span>
        <span class="focus-chip">Next focus: <strong>{escape(str(archetype.get("opportunity", "N/A")))}</strong></span>
      </div>
      {distinction_html}
    </section>
    <section>
      <h2>Trait scores</h2>
      <p class="muted">Scores compare eligible teammates in this match. Enemy metrics are context only and do not enter ranking.</p>
      <div class="scores">{score_cards}</div>
      <p class="muted">Positioning score reflects rifle movement discipline and utility deaths per round.</p>
    </section>
    <section>
      <h2>Performance snapshot</h2>
      <div class="stats">{context["stats_cards"]}</div>
    </section>
    <section>
      <h2>Match diagnosis</h2>
      {context["diagnosis_html"]}
    </section>
    <section>
      <h2>Weapon and hit review</h2>
      <div class="columns">
        <div class="panel"><h3>Where your shots landed</h3>{context["hit_model_html"]}</div>
        <div class="panel">
          <h3>Weapon playstyle</h3>
          <table><thead><tr><th>Category</th><th>Shots</th><th>Moving</th><th>Rate</th></tr></thead><tbody>{context["weapon_playstyle_rows"]}</tbody></table>
          <h3 style="margin-top:24px">Pistol range</h3>
          <p class="muted">Average kill distance: {context["pistol_distance_display"]}</p>
          <p class="muted">Close: {context["pistol_distance_buckets"]["close"]} · Medium: {context["pistol_distance_buckets"]["medium"]} · Long: {context["pistol_distance_buckets"]["long"]}</p>
        </div>
      </div>
    </section>
    <details>
      <summary>View detailed data</summary>
      <div class="details-content">
        <section><div class="chart">{context["chart_html"]}</div></section>
        <section>
          <h2>Aim deviation on kills</h2>
          <p>Average deviation: {context["average_deviation_html"]} degrees (lower is better).</p>
          <h3>By weapon</h3>
          <table><thead><tr><th>Weapon</th><th>Average deviation</th><th>Sample count</th></tr></thead><tbody>{context["weapon_deviation_rows"]}</tbody></table>
        </section>
        {context["suspected_fire_section_html"]}
        <section id="flashbang-table">
          <h2>Flashbang results</h2>
          <p>{context["flash_count"]} thrown · {context["enemy_blinds"]} enemies blinded · {context["teammate_blinds"]} teammates blinded · {context["self_blinds"]} self-blinds.</p>
          <table><thead><tr><th>Enemies</th><th>Teammates</th><th>Self</th><th>Outcome</th></tr></thead><tbody>{context["flash_detail_rows"]}</tbody></table>
        </section>
      </div>
    </details>
  </main>
  <script>
    document.querySelectorAll('.diagnosis-card-link').forEach(card => {{
      card.addEventListener('click', event => {{
        event.preventDefault();
        const target = document.getElementById(card.getAttribute('href')?.slice(1));
        if (!target) return;
        const details = target.closest('details');
        if (details) details.open = true;
        requestAnimationFrame(() => target.scrollIntoView({{ behavior: 'smooth', block: 'start' }}));
      }});
    }});
  </script>
</body>
</html>"""