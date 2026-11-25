"""Bridge the Streamlit GUI to the canonical report CLI."""

from collections.abc import Callable
import os
from pathlib import Path
import subprocess
import sys

from cs2_report.localization import DEFAULT_LOCALE, SUPPORTED_LOCALES, report_output_paths


ProgressCallback = Callable[[float, str], None] | None


def _run_report(
    demo_path: Path,
    player_input: str,
    version: str,
    progress_callback: ProgressCallback,
    locale: str = DEFAULT_LOCALE,
) -> dict[str, str]:
    demo = Path(demo_path).expanduser().resolve()
    script = Path(__file__).with_name("report.py")
    if version not in {"1.0", "2.0", "all"}:
        raise ValueError("version must be '1.0', '2.0', or 'all'.")
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")

    env = os.environ.copy()
    env["CS2_REPORT_PROGRESS"] = "1"
    process = subprocess.Popen(
        [
            sys.executable, str(script), "--demo", str(demo),
            "--player", player_input.strip(), "--report-version", version,
            "--locale", locale,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    output = []
    assert process.stdout is not None
    for line in process.stdout:
        if line.startswith("CS2_PROGRESS|"):
            if progress_callback:
                _, fraction, message = line.rstrip("\r\n").split("|", 2)
                progress_callback(float(fraction), message)
        else:
            output.append(line)

    if process.wait() != 0:
        raise RuntimeError("".join(output).strip() or "Report generation failed.")

    versions = ("1.0", "2.0") if version == "all" else (version,)
    reports = {}
    for report_version in versions:
        _, html_path = report_output_paths(demo, report_version, locale)
        if not html_path.is_file():
            raise RuntimeError(f"Report generation did not create {html_path.name}.")
        reports[report_version] = html_path.read_text(encoding="utf-8")
    return reports


def run_analysis(
    demo_path: Path,
    player_input: str,
    progress_callback: ProgressCallback = None,
    report_version: str = "1.0",
    locale: str = DEFAULT_LOCALE,
) -> str:
    """Generate one version and return its HTML for existing GUI integrations."""
    if report_version not in {"1.0", "2.0"}:
        raise ValueError("Use '1.0' or '2.0' here; use run_analysis_versions() for both.")
    reports = _run_report(demo_path, player_input, report_version, progress_callback, locale)
    return reports[report_version]


def run_analysis_versions(
    demo_path: Path,
    player_input: str,
    progress_callback: ProgressCallback = None,
    locale: str = DEFAULT_LOCALE,
) -> dict[str, str]:
    """Generate both report versions in one demo-analysis run."""
    return _run_report(demo_path, player_input, "all", progress_callback, locale)
