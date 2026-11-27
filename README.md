# CS2 Report

CS2 Report is a Streamlit application that analyzes Counter-Strike 2 demo files and generates detailed player performance reports with interactive visualizations.

## Features

- **Interactive Bullet Heatmaps**: Visualize where players hit their targets
- **Weapon Categorization**: Group hits by weapon type for better analysis
- **Detailed Statistics**: Comprehensive player performance metrics
- **500MB Demo File Support**: Handle large demo files efficiently

## Run on Windows

From the repository root, create a Python 3.12 environment and install the app dependencies.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "awpy==3.3.0" polars plotly "streamlit>=1.67"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

You can also run `run_streamlit_app.bat` from an environment with the dependencies installed.

1. Upload a Counter-Strike 2 `.dem` file.
2. Choose a player from the roster and select the report language in the header.
3. Generate the report, switch between Report 2.0 and Report 1.0, or download the selected version.

### Report language

Choose English, Danish, or Russian before generating a report. The selected
language applies to both report versions and their HTML downloads. If you
change languages after generating a report, generate it again for the same
player. The app retains the uploaded demo and player selection.

For CLI reports, add `--locale en`, `--locale da-DK`, or `--locale ru-RU`.
Use `--report-version all` to generate both versions. On Windows use
`python -X utf8 report.py` when piping or redirecting CLI output. English
keeps the original filenames. Danish and Russian filenames include the locale.
Report numbers use decimal points in every language. Streamlit's built-in
uploader controls and raw technical error details can still appear in English.
App and report messages fall back to English when a locale lacks a message.

To add a locale, copy `cs2_report/locales/en.json` to the new locale's JSON
file, translate the values while keeping each format placeholder, and register
the locale and its display name in `cs2_report/localization.py`. Run the
localization tests and check both rendered report versions. Compare K/D, ADR,
and trait scores with the English report and check that the app preview and
download use the same language.

## Repository layout

| Path | Contents |
| --- | --- |
| `app.py`, `run_streamlit_app.bat` | Streamlit app and Windows launcher |
| `report.py`, `analysis_wrapper.py` | Report CLI and the adapter used by the app |
| `cs2_report/` | Demo parsing, analysis, renderers, and locale catalogs |
| `assets/` | App artwork and report hit-map images |
| `docs/` | Project roadmap, architecture, and report design notes |
| `scripts/` | Manual diagnostics and demo inspection |
| `tests/` | Automated tests |
| `.streamlit/config.toml` | Streamlit configuration |

Read the [architecture overview](docs/PROJECT_FLOW.md) or [roadmap](docs/PROJECT_ROADMAP.md).

## Development

Run these commands from the repository root.

```powershell
python -m unittest discover -s tests -v
python -m scripts.check_locales
```

To inspect Awpy tables, place a demo named `test.dem` at the repository root and run `python -m scripts.explore`. The other scripts are manual diagnostics.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.