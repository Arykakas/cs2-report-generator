from pathlib import Path
from pathlib import Path
from html import escape
import tempfile

import streamlit as st

from analysis_wrapper import run_analysis


def _reset_demo_state() -> None:
    for key in ("player_options", "player_options_error", "selected_player", "report_result"):
        st.session_state.pop(key, None)


def _clear_report() -> None:
    st.session_state.pop("report_result", None)


st.set_page_config(
    page_title="CS2 Match Analyzer",
    page_icon=":material/sports_esports:",
    layout="wide",
)

st.markdown(
    """
    <style>
      .match-hero {
        position: relative;
        overflow: hidden;
        margin: .25rem 0 1.4rem;
        padding: 1.7rem 2rem;
        border: 1px solid #304254;
        border-radius: 16px;
        background: linear-gradient(115deg, #172333 0%, #111c29 64%, #172719 100%);
      }
      .match-hero:after {
        content: "";
        position: absolute;
        top: -90px;
        right: -35px;
        width: 230px;
        height: 230px;
        border: 1px solid #b7f34a22;
        border-radius: 50%;
        box-shadow: 0 0 0 24px #b7f34a0a, 0 0 0 50px #b7f34a08;
      }
      .hero-kicker {
        margin: 0 0 .55rem;
        color: #b7f34a;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .19em;
        text-transform: uppercase;
      }
      .match-hero h1 {
        margin: 0;
        color: #f3f7fb;
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.05;
        letter-spacing: -.045em;
      }
      .match-hero p:last-child {
        margin: .7rem 0 0;
        color: #9aabba;
        font-size: .98rem;
      }
      .step-label {
        margin-bottom: .2rem;
        color: #b7f34a;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
      }
      .file-meta {
        margin-top: .65rem;
        color: #9aabba;
        font-size: .85rem;
      }
      .setup-note {
        padding: .8rem 1rem;
        border-left: 3px solid #b7f34a;
        border-radius: 0 8px 8px 0;
        background: #b7f34a0c;
        color: #c7d2dc;
        font-size: .9rem;
      }
      .report-ready {
        margin-top: 1rem;
        padding: 1.1rem 1.3rem;
        border: 1px solid #36523a;
        border-radius: 12px;
        background: #14231b;
      }
      @media (max-width: 700px) {
        .match-hero { padding: 1.35rem 1.2rem; }
      }
    </style>
    <div class="match-hero">
      <p class="hero-kicker">Counter-Strike 2 / Performance lab</p>
      <h1>Match intelligence</h1>
      <p>Upload a demo, lock in a player, and get a focused tactical breakdown.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("LOCAL DEMO ANALYSIS  /  NO STEAM SIGN-IN REQUIRED")

upload_column, player_column = st.columns([1.05, 0.95], gap="large")
demo_file = None
selected_player = None

with upload_column:
    with st.container(border=True):
        st.markdown('<div class="step-label">01 / Match file</div>', unsafe_allow_html=True)
        st.subheader("Upload demo")
        demo_file = st.file_uploader(
            "Choose a Counter-Strike 2 demo",
            type=["dem"],
            key="demo_upload",
            on_change=_reset_demo_state,
            help="The uploaded file is processed locally by this app.",
        )
        if demo_file is None:
            st.markdown(
                '<div class="file-meta">Supported format: .dem · Maximum size: 500 MB</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="file-meta">Loaded: <strong>{escape(demo_file.name)}</strong> · '
                f'{demo_file.size / (1024 * 1024):.1f} MB</div>',
                unsafe_allow_html=True,
            )

with player_column:
    with st.container(border=True):
        st.markdown('<div class="step-label">02 / Player identity</div>', unsafe_allow_html=True)
        st.subheader("Select player")

        if demo_file is None:
            st.markdown(
                '<div class="setup-note">Upload a match demo to inspect its player roster.</div>',
                unsafe_allow_html=True,
            )
        else:
            if "player_options" not in st.session_state:
                st.session_state.player_options = {}
                st.session_state.player_options_error = None
                with st.spinner("Scanning demo roster..."):
                    try:
                        from awpy import Demo

                        with tempfile.TemporaryDirectory() as temp_dir:
                            upload_name = Path(demo_file.name).name or "uploaded.dem"
                            temp_demo_path = Path(temp_dir) / upload_name
                            temp_demo_path.write_bytes(demo_file.getbuffer())
                            demo = Demo(temp_demo_path)
                            demo.load("shots")
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
                    except Exception as exc:
                        st.session_state.player_options_error = str(exc)

            if st.session_state.get("player_options_error"):
                st.error(
                    f"Could not read the demo roster: {st.session_state.player_options_error}",
                    title="Roster scan failed",
                )
            else:
                player_options = st.session_state.get("player_options", {})
                if player_options:
                    selected_player = st.selectbox(
                        "Choose a player",
                        options=list(player_options),
                        format_func=lambda steamid: f"{player_options[steamid]}  ·  {steamid}",
                        key="selected_player",
                        on_change=_clear_report,
                    )
                    st.markdown(
                        '<div class="file-meta">Player ID is included to distinguish duplicate names.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning("No players with recorded shots were found in this demo.")

st.space("small")
generate_report = st.button(
    "Generate match report",
    type="primary",
    icon=":material/analytics:",
    width="stretch",
    disabled=demo_file is None or selected_player is None,
)

if demo_file is None or selected_player is None:
    st.caption("Upload a demo and select a player to enable report generation.")

if generate_report:
    st.session_state.pop("report_result", None)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            upload_name = Path(demo_file.name).name or "uploaded.dem"
            temp_demo_path = Path(temp_dir) / upload_name
            temp_demo_path.write_bytes(demo_file.getbuffer())

            with st.spinner("Parsing match data and building the report..."):
                html_report = run_analysis(temp_demo_path, selected_player)

        st.session_state.report_result = {
            "html": html_report,
            "file_name": f"{Path(demo_file.name).stem or 'match'}_report.html",
            "player_name": st.session_state.player_options[selected_player],
        }
    except Exception as exc:
        st.error(str(exc), title="Report generation failed")
        with st.expander("Technical details"):
            st.exception(exc)

report_result = st.session_state.get("report_result")
if report_result:
    with st.container(border=True):
        st.success(f"Report ready for {report_result['player_name']}.")
        st.download_button(
            "Download HTML report",
            data=report_result["html"],
            file_name=report_result["file_name"],
            mime="text/html",
            icon=":material/download:",
            width="stretch",
            on_click="ignore",
        )

with st.expander("About this tool"):
    st.write(
        "The report analyzes weapon movement, aim deviation, utility deaths, "
        "flashbang effects, and hit distribution from your uploaded CS2 demo."
    )
