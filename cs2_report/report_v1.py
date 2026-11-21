"""Report 1.0 text and HTML assembly."""

from .rendering.html import render_html_report
from .report_common import common_text_lines


def generate(context: dict) -> tuple[str, str]:
    """Build the compatible Report 1.0 outputs from shared analysis results."""
    lines = ["SUMMARY", *context["summary_sentences"], ""]
    lines.extend(common_text_lines(context))
    return "\n".join(lines), render_html_report(context)
