"""Report 2.0 coaching-oriented text and HTML assembly."""

from .rendering.html_v2 import render_html_report_v2
from .report_common import common_text_lines


def generate(context: dict) -> tuple[str, str]:
    """Build the standalone Report 2.0 outputs."""
    archetype = context["archetype_analysis"]
    scores = archetype["scores"]
    lines = [
        "CS2 MATCH REPORT 2.0",
        "",
        f"Player archetype: {archetype['archetype']}",
        archetype["summary"],
        "",
        "TRAIT SCORES",
        f"Aggression: {scores['aggression']:.0f}/100",
        f"Precision: {scores['precision']:.0f}/100",
        f"Utility: {scores['utility']:.0f}/100",
        f"Positioning: {scores['positioning']:.0f}/100",
        "",
    ]
    lines.extend(common_text_lines(context))
    return "\n".join(lines), render_html_report_v2(context)
