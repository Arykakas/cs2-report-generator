"""Run the canonical report generator and return its HTML for the GUI."""

from pathlib import Path
import subprocess
import sys


def run_analysis(demo_path: Path, player_input: str) -> str:
    """Generate a full report with report.py and return the generated HTML."""
    resolved_demo = Path(demo_path).expanduser().resolve()
    report_script = Path(__file__).with_name("report.py")
    html_path = resolved_demo.with_name(f"{resolved_demo.stem}_report.html")

    result = subprocess.run(
        [
            sys.executable,
            str(report_script),
            "--demo",
            str(resolved_demo),
            "--player",
            player_input.strip(),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or "Report generation failed without an error message.")

    if not html_path.is_file():
        raise RuntimeError("report.py completed but did not create the expected HTML report.")

    return html_path.read_text(encoding="utf-8")
