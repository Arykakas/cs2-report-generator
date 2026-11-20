"""Run the canonical report generator and return its HTML for the GUI."""

from pathlib import Path
import os
import subprocess
import sys
from collections.abc import Callable


def run_analysis(
    demo_path: Path,
    player_input: str,
    progress_callback: Callable[[float, str], None] | None = None,
) -> str:
    """Generate a full report with report.py and return the generated HTML."""
    resolved_demo = Path(demo_path).expanduser().resolve()
    report_script = Path(__file__).with_name("report.py")
    html_path = resolved_demo.with_name(f"{resolved_demo.stem}_report.html")

    process_env = os.environ.copy()
    process_env["CS2_REPORT_PROGRESS"] = "1"
    process = subprocess.Popen(
        [
            sys.executable,
            str(report_script),
            "--demo",
            str(resolved_demo),
            "--player",
            player_input.strip(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=process_env,
    )

    output_lines = []
    assert process.stdout is not None
    for line in process.stdout:
        if line.startswith("CS2_PROGRESS|"):
            if progress_callback is not None:
                _, fraction, message = line.rstrip("\r\n").split("|", 2)
                progress_callback(float(fraction), message)
        else:
            output_lines.append(line)

    return_code = process.wait()
    if return_code != 0:
        detail = "".join(output_lines).strip()
        raise RuntimeError(detail or "Report generation failed without an error message.")

    if not html_path.is_file():
        raise RuntimeError("report.py completed but did not create the expected HTML report.")

    return html_path.read_text(encoding="utf-8")
