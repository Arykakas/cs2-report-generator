from pathlib import Path
from html import escape
from base64 import b64encode
import importlib
import tempfile

import streamlit as st

import analysis_wrapper as report_runner

# Streamlit can keep locally imported modules cached across script reruns.
report_runner = importlib.reload(report_runner)


def _reset_demo_state() -> None:
    for key in ("player_options", "player_options_error", "selected_player", "report_result", "preview_report_version"):
        st.session_state.pop(key, None)


def _clear_report() -> None:
    st.session_state.pop("report_result", None)
    st.session_state.pop("preview_report_version", None)


def _scan_player_roster(demo_file) -> None:
    """Read the uploaded demo once and store players for the dropdown."""
    st.session_state.player_options = {}
    st.session_state.player_options_error = None

    progress = st.progress(0.08, text="Opening demo file")
    try:
        from awpy import Demo

        with tempfile.TemporaryDirectory() as temp_dir:
            upload_name = Path(demo_file.name).name or "uploaded.dem"
            temp_demo_path = Path(temp_dir) / upload_name
            temp_demo_path.write_bytes(demo_file.getbuffer())

            progress.progress(0.28, text="Parsing match and player data")
            demo = Demo(temp_demo_path)
            demo.load("shots")
            progress.progress(0.86, text="Preparing the player selector")
            player_rows = (
                demo.shots.select("name", "steamid")
                .drop_nulls()
                .unique()
                .sort(["name", "steamid"])
                .to_dicts()
            )

        st.session_state.player_options = {
            str(row["steamid"]): str(row["name"])
            for row in player_rows
        }
        progress.progress(1.0, text="Roster ready")
    except Exception as exc:
        st.session_state.player_options_error = str(exc)
    finally:
        progress.empty()


st.set_page_config(
    page_title="CS2 Match Analyzer",
    page_icon=":material/sports_esports:",
    layout="wide",
)

operator_svg = Path(__file__).with_name("tactical_operator.svg").read_bytes()
operator_data_uri = "data:image/svg+xml;base64," + b64encode(operator_svg).decode("ascii")
radar_svg = Path(__file__).with_name("tactical_radar_match_insights.svg").read_bytes()
radar_data_uri = "data:image/svg+xml;base64," + b64encode(radar_svg).decode("ascii")
st.html(
    f'<div class="arena-background-glow" aria-hidden="true"></div>'
    f'<img class="radar-backdrop" src="{radar_data_uri}" alt="" aria-hidden="true">'
    f'<img class="operator-backdrop" src="{operator_data_uri}" alt="" aria-hidden="true">'
)

st.html(
    """
    <style>
      .arena-background-glow { position: fixed; z-index: 0; top: 12vh; right: -18vw; width: 58vw; height: 74vh; border-radius: 50%; background: radial-gradient(ellipse, #7548c522 0%, #7548c510 42%, transparent 72%); pointer-events: none; }
      .radar-backdrop { position: fixed; z-index: 0; top: 50%; left: -18px; width: min(25vw, 430px); height: 90vh; transform: translateY(-50%); object-fit: contain; object-position: left center; opacity: .34; filter: drop-shadow(0 0 30px #8b5cf622); mask-image: linear-gradient(90deg, #000 0%, #000 68%, transparent 100%); pointer-events: none; }
      .operator-backdrop { position: fixed; z-index: 0; top: 5vh; right: -3vw; width: min(45vw, 630px); height: 92vh; object-fit: contain; object-position: right center; opacity: .2; filter: drop-shadow(0 0 38px #8b5cf633); mask-image: linear-gradient(90deg, transparent 0%, #000 28%, #000 100%); pointer-events: none; }
      .arena-shell { position: relative; z-index: 1; max-width: 980px; margin: 0 auto 1.4rem; }
      .arena-topline { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.2rem; }
      .arena-brand { color: #f1f5f9; font: 600 .82rem 'Fira Code', monospace; letter-spacing: .12em; text-transform: uppercase; }
      .arena-status { display: inline-flex; align-items: center; gap: .5rem; border: 1px solid #29354a; border-radius: 999px; padding: .42rem .72rem; color: #aab7c9; font: 500 .68rem 'Fira Code', monospace; letter-spacing: .08em; text-transform: uppercase; }
      .arena-status::before { content: ''; width: .45rem; height: .45rem; border-radius: 50%; background: #34d399; box-shadow: 0 0 12px #34d39988; }
      .arena-hero { position: relative; overflow: hidden; padding: clamp(1.55rem, 4vw, 3rem); border: 1px solid #29354a; border-radius: 22px; background: linear-gradient(90deg, #151b2bf5 0%, #151b2bdc 53%, #151b2b78 100%), radial-gradient(ellipse at 85% 0%, #7c3aed35 0, transparent 42%); }
      .arena-hero::after { content: ''; position: absolute; width: 240px; height: 240px; right: -95px; bottom: -155px; border: 1px solid #a78bfa35; border-radius: 50%; box-shadow: 0 0 0 28px #a78bfa0c, 0 0 0 58px #a78bfa08; pointer-events: none; }
      .arena-eyebrow { margin: 0 0 .8rem; color: #a78bfa; font: 600 .7rem 'Fira Code', monospace; letter-spacing: .18em; text-transform: uppercase; }
      .arena-title { max-width: 700px; margin: 0; color: #f8fafc; font: 700 clamp(2rem, 5vw, 3.45rem)/1.04 'Fira Sans', sans-serif; letter-spacing: -.045em; }
      .arena-title span { color: #a78bfa; }
      .arena-copy { max-width: 590px; margin: 1rem 0 0; color: #a4afc0; font: 400 1rem/1.65 'Fira Sans', sans-serif; }
      .arena-perks { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.35rem; }
      .arena-perk { border: 1px solid #303b50; border-radius: 7px; padding: .4rem .62rem; color: #c4cede; background: #0c1220a8; font: 500 .68rem 'Fira Code', monospace; letter-spacing: .035em; }
      .st-key-upload_stage, .st-key-analysis_complete { position: relative; z-index: 1; border-color: #303b50; border-radius: 18px; background: linear-gradient(145deg, #151b2aeb, #111724e8); box-shadow: 0 20px 55px #03071245; }
      .st-key-upload_stage { padding: clamp(1.1rem, 3vw, 2rem); }
      .st-key-analysis_complete { padding: 1rem clamp(1rem, 2.5vw, 1.5rem); border-color: #354158; background: linear-gradient(140deg, #151c2beb, #111724e8); }
      .upload-intro { margin-bottom: .4rem; }
      .upload-step { margin: 0 0 .45rem; color: #fb7185; font: 600 .68rem 'Fira Code', monospace; letter-spacing: .12em; text-transform: uppercase; }
      .upload-title { margin: 0; color: #f3f6fb; font: 600 1.25rem 'Fira Sans', sans-serif; }
      .upload-hint { margin: .35rem 0 1rem; color: #96a3b7; font-size: .9rem; }
      .file-summary { display: flex; align-items: center; gap: .75rem; margin: .75rem 0 1rem; border: 1px solid #33415a; border-radius: 11px; padding: .8rem .95rem; background: #0c1320; color: #d6deea; }
      .file-token { display: inline-grid; width: 2.35rem; height: 2.35rem; place-items: center; border: 1px solid #7042c7; border-radius: 8px; background: #7c3aed22; color: #c4b5fd; font: 600 .65rem 'Fira Code', monospace; }
      .file-summary strong { color: #f8fafc; }
      .file-summary small { display: block; margin-top: .15rem; color: #94a3b8; }
      .complete-header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: .8rem; }
      .complete-heading { margin: 0; color: #f8fafc; font: 650 1.15rem 'Fira Sans', sans-serif; }
      .complete-copy { margin: .25rem 0 0; color: #9ba9bc; font-size: .86rem; }
      .complete-state { flex: none; border: 1px solid #24624c; border-radius: 999px; padding: .35rem .65rem; color: #86efac; background: #123326; font: 600 .65rem 'Fira Code', monospace; letter-spacing: .08em; text-transform: uppercase; }
      .complete-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem .8rem; margin: .8rem 0 1rem; border-top: 1px solid #293449; padding-top: .75rem; color: #dbe4ef; font-size: .88rem; }
      .complete-meta span { color: #8492a7; font: 500 .65rem 'Fira Code', monospace; letter-spacing: .08em; }
      .complete-meta strong { color: #eef2f8; font-weight: 600; }
      .complete-separator { color: #465269; }
      .st-key-download_report button { border-color: #38bdf8; background: #38bdf8; color: #0b1220; font-weight: 700; }
      .st-key-download_report button:hover { border-color: #7dd3fc; background: #7dd3fc; color: #0b1220; }
      .st-key-generate_report button { min-height: 3rem; font-weight: 700; letter-spacing: .025em; }
      .st-key-generate_report button:disabled { opacity: 1; }
      @media (max-width: 640px) {
        .arena-topline { align-items: flex-start; flex-direction: column; }
        .arena-hero { border-radius: 16px; }
        .radar-backdrop { left: -24vw; width: 58vw; opacity: .14; }
        .operator-backdrop { right: -25vw; width: 78vw; opacity: .12; }
      }
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; }
      }
    </style>
    <div class="arena-shell">
      <div class="arena-topline">
        <div class="arena-brand">CS2 // Match analyzer</div>
        <div class="arena-status">Local analysis · No Steam sign-in</div>
      </div>
      <header class="arena-hero">
        <p class="arena-eyebrow">Post-match performance lab</p>
        <h1 class="arena-title">Review the round.<br><span>Own the next one.</span></h1>
        <p class="arena-copy">Drop in a Counter-Strike 2 demo, pick your player, and get a focused breakdown of movement, aim, utility, and hit distribution.</p>
        <div class="arena-perks">
          <span class="arena-perk">MOVEMENT ANALYSIS</span>
          <span class="arena-perk">AIM DEVIATION</span>
          <span class="arena-perk">UTILITY IMPACT</span>
          <span class="arena-perk">HIT MAP</span>
        </div>
      </header>
    </div>
    """
)

st.space("small")
outer_left, center, outer_right = st.columns([0.7, 2.6, 0.7])
with center:
    with st.container(border=True, key="upload_stage"):
        st.markdown(
            '<div class="upload-intro"><p class="upload-step">01 / Match file</p>'
            '<p class="upload-title">Upload your demo</p>'
            '<p class="upload-hint">Drag a <strong>.dem</strong> file into the drop zone or browse from your device. Up to 500 MB.</p></div>',
            unsafe_allow_html=True,
        )
        demo_file = st.file_uploader(
            "Choose a Counter-Strike 2 demo",
            type=["dem"],
            key="demo_upload",
            on_change=_reset_demo_state,
            help="The uploaded file is processed locally by this app.",
        )

        selected_player = None
        if demo_file is not None:
            if "player_options" not in st.session_state:
                with st.status("Parsing demo roster", expanded=False) as roster_status:
                    _scan_player_roster(demo_file)
                    if st.session_state.player_options_error:
                        roster_status.update(label="Roster scan failed", state="error")
                    else:
                        roster_status.update(label="Player roster ready", state="complete")

            st.markdown(
                f'<div class="file-summary"><span class="file-token">DEM</span><div><strong>{escape(demo_file.name)}</strong>'
                f'<small>{demo_file.size / (1024 * 1024):.1f} MB · Demo loaded</small></div></div>',
                unsafe_allow_html=True,
            )

            if st.session_state.get("player_options_error"):
                st.error(
                    f"Could not read the demo roster: {st.session_state.player_options_error}",
                    title="Roster scan failed",
                )
            else:
                player_options = st.session_state.get("player_options", {})
                if player_options:
                    st.markdown('<p class="upload-step">02 / Player identity</p>', unsafe_allow_html=True)
                    selected_player = st.selectbox(
                        "Choose a player",
                        options=list(player_options),
                        format_func=lambda steamid: f"{player_options[steamid]}  ·  {steamid}",
                        key="selected_player",
                        on_change=_clear_report,
                    )
                    st.caption("Steam ID is shown to distinguish players with duplicate names.")
                else:
                    st.warning("No players with recorded shots were found in this demo.")

        can_generate = demo_file is not None and selected_player is not None
        button_progress = st.empty()
        generate_report = st.button(
            "Generate match report",
            type="primary",
            icon=":material/analytics:",
            width="stretch",
            disabled=not can_generate,
            key="generate_report",
        )

if generate_report:
    st.session_state.pop("report_result", None)
    st.session_state.pop("preview_report_version", None)

    def update_button_progress(fraction: float, _message: str = "") -> None:
        percent = max(0, min(100, round(fraction * 100)))
        button_progress.html(
            f"""
            <style>
              .st-key-generate_report button {{
                position: relative;
                overflow: hidden;
                border-color: #F43F5E !important;
                color: transparent !important;
                background: linear-gradient(90deg, #F43F5E 0%, #F43F5E {percent}%, #F8FAFC {percent}%, #F8FAFC 100%) !important;
                transition: background 180ms ease-out;
              }}
              .st-key-generate_report button::after {{
                content: "ANALYZING MATCH · {percent}%";
                position: absolute;
                inset: 0;
                display: grid;
                place-items: center;
                color: #10131b;
                font-size: .78rem;
                font-weight: 750;
                letter-spacing: .055em;
              }}
            </style>
            """,
        )

    try:
        update_button_progress(0.03)
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_name = Path(demo_file.name).name or "uploaded.dem"
            temp_demo_path = Path(temp_dir) / upload_name
            temp_demo_path.write_bytes(demo_file.getbuffer())
            html_reports = report_runner.run_analysis_versions(
                temp_demo_path,
                selected_player,
                progress_callback=update_button_progress,
            )

        update_button_progress(1.0)
        button_progress.empty()
        st.session_state.report_result = {
            "html_reports": html_reports,
            "file_names": {
                "1.0": f"{Path(demo_file.name).stem or 'match'}_report.html",
                "2.0": f"{Path(demo_file.name).stem or 'match'}_report_2.0.html",
            },
            "player_name": st.session_state.player_options[selected_player],
            "demo_name": Path(demo_file.name).name,
        }
    except Exception as exc:
        button_progress.empty()
        st.error(str(exc), title="Report generation failed")
        with st.expander("Technical details"):
            st.exception(exc)

report_result = st.session_state.get("report_result")
if report_result and "html_reports" not in report_result:
    # Drop pre-version-picker results retained by an already-open app session.
    st.session_state.pop("report_result", None)
    report_result = None
if report_result:
    st.space("small")
    _, result_center, _ = st.columns([0.7, 2.6, 0.7])
    with result_center:
        with st.container(border=True, key="analysis_complete"):
            st.markdown(
                '<div class="complete-header"><div>'
                '<p class="upload-step">03 / Match review</p>'
                '<p class="complete-heading">Report ready</p>'
                '<p class="complete-copy">Your tactical breakdown is ready to save.</p>'
                '</div><span class="complete-state">Analysis complete</span></div>'
                f'<div class="complete-meta"><span>MATCH</span><strong>{escape(report_result["demo_name"])}</strong>'
                '<i class="complete-separator">/</i><span>PLAYER</span>'
                f'<strong>{escape(report_result["player_name"])}</strong></div>',
                unsafe_allow_html=True,
            )
    report_version = st.segmented_control(
        "Report version",
        options=("2.0", "1.0"),
        default="2.0",
        format_func=lambda version: f"Report {version}",
        key="preview_report_version",
    )
    if report_version:
        st.iframe(
            report_result["html_reports"][report_version],
            width="stretch",
            height="content",
            alt=f"Report {report_version} for {report_result['player_name']}",
        )
        with st.container(horizontal=True, horizontal_alignment="right"):
            st.download_button(
                "Download report",
                data=report_result["html_reports"][report_version],
                file_name=report_result["file_names"][report_version],
                mime="text/html",
                icon=":material/download:",
                width="content",
                key="download_report",
                on_click="ignore",
            )


st.caption("CS2 MATCH ANALYZER  /  ANALYSIS RUNS LOCALLY ON THIS MACHINE")
