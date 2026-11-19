import streamlit as st
from pathlib import Path
import tempfile

from analysis_wrapper import run_analysis

# Set page config for dark theme
st.set_page_config(
    page_title="CS2 Match Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for gaming theme
st.markdown("""
<style>
    :root {
        --primary-color: #10b981;
        --secondary-color: #3b82f6;
        --accent-color: #8b5cf6;
        --dark-bg: #0f172a;
        --darker-bg: #0c111f;
        --card-bg: #1e293b;
        --text-light: #f8fafc;
        --text-gray: #94a3b8;
    }
    
    body {
        background-color: var(--dark-bg);
        color: var(--text-light);
    }
    
    .stApp {
        background-color: var(--dark-bg);
    }
    
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #059669;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
    }
    
    .stTextInput>div>div>input {
        background-color: var(--card-bg);
        color: var(--text-light);
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    .stFileUploader>div>button {
        background-color: var(--secondary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stFileUploader>div>button:hover {
        background-color: #2563eb;
    }
    
    .reportview-container {
        background-color: var(--dark-bg);
    }
    
    h1, h2, h3 {
        color: var(--text-light);
    }
    
    .stMarkdown {
        color: var(--text-light);
    }
    
    .stSelectbox>div>div>select {
        background-color: var(--card-bg);
        color: var(--text-light);
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    .st-expander > .st-expander > .st-expander-header {
        background-color: var(--card-bg);
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    .st-progress {
        background-color: #1e293b;
        border-radius: 4px;
        height: 10px;
    }
    
    .st-progress > div {
        background-color: var(--primary-color);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# App title with gaming vibe
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h1>🎯 CS2 Match Analyzer</h1>
    <p style="color: #94a3b8;">Comprehensive tactical performance analysis for Counter-Strike 2</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for main inputs
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Demo File")
    demo_file = st.file_uploader("Upload CS2 Demo File (.dem)", type=['dem'])
    
    st.subheader("👤 Player Selection")
    
    # If a demo file is uploaded, we can show player selection
    if demo_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save uploaded file to temp directory
                temp_demo_path = Path(temp_dir) / demo_file.name
                with open(temp_demo_path, "wb") as f:
                    f.write(demo_file.getbuffer())
                
                # Load demo and get player list
                from awpy import Demo
                demo = Demo(temp_demo_path)
                demo.load("shots", "kills", "grenades", "blinds")
                
                # Get unique player names from shots
                player_names = demo.shots.select("name").unique().to_series().to_list()
                
                if player_names:
                    # Remove None values and sort players
                    player_names = [name for name in player_names if name is not None]
                    player_names.sort()
                    
                    selected_player = st.selectbox(
                        "Select Player from Demo",
                        options=player_names,
                        index=0 if player_names else None,
                        placeholder="Choose a player from the demo"
                    )
                else:
                    st.warning("No players found in the demo file.")
                    selected_player = st.text_input("Enter Player Name", placeholder="Enter player name as shown in demo (or Steam ID)")
                    
            except Exception as e:
                st.error(f"Error reading demo file: {str(e)}")
                selected_player = st.text_input("Enter Player Name", placeholder="Enter player name as shown in demo (or Steam ID)")
    else:
        selected_player = st.text_input("Enter Player Name", placeholder="Enter player name as shown in demo (or Steam ID)")

with col2:
    st.subheader("💾 Output Settings")
    st.caption("The generated full HTML report will be available to download here.")
    
    # Add a placeholder for the actual analysis result
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Generate Report", width="stretch"):
        if demo_file is None:
            st.error("Please upload a demo file")
        elif not player_name:
            st.error("Please enter player name")
        else:
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Save uploaded file to temp directory
                    upload_name = Path(demo_file.name).name or "uploaded.dem"
                    temp_demo_path = Path(temp_dir) / upload_name
                    with open(temp_demo_path, "wb") as f:
                        f.write(demo_file.getbuffer())
                    
                    with st.spinner("Parsing the demo and generating the full report..."):
                        html_report = run_analysis(temp_demo_path, selected_player)
                    
                    st.success("Report generated successfully!")
                    
                    # Provide download link
                    st.download_button(
                        label="📥 Download Report",
                        data=html_report,
                        file_name=f"{temp_demo_path.stem}_report.html",
                        mime="text/html"
                    )
                            
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.exception(e)

# Add some information about the tool
st.markdown("---")
st.subheader("ℹ️ About CS2 Match Analyzer")
st.markdown("""
This tool analyzes CS2 demo files to provide detailed tactical performance insights including:
- Weapon usage patterns and kill distances  
- Movement while shooting analysis
- Aim deviation metrics
- Flashbang effects and utility usage
- Utility usage detection

**Note**: For best results, use the Steam profile URL/ID for accurate player identification, as names can change in future matches.

**File Upload Limit**: The system now supports demo files up to 500MB in size (previously limited to 200MB).
""")

# Add a footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8;'>CS2 Match Analyzer v1.0 | Competitive Gaming Analytics</p>", unsafe_allow_html=True)
