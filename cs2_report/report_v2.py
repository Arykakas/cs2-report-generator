"""Report 2.0 coaching-oriented text and HTML assembly."""

from .rendering.html_v2 import render_html_report_v2
from .localization import translate
from .report_common import common_text_lines


def generate(context: dict) -> tuple[str, str]:
    """Build the standalone Report 2.0 outputs."""
    archetype = context["archetype_analysis"]
    scores = archetype["scores"]
    locale = context.get("locale", "en")
    tied_distinctions = archetype.get("tied_distinctions", [])
    distinction_text = (
        translate(locale, "report.v2.tied_distinctions", traits=", ".join(tied_distinctions))
        if tied_distinctions
        else translate(locale, "report.v2.tied_none")
    )
    lines = [
        translate(locale, "report.v2.text_title"),
        "",
        f"{translate(locale, 'report.v2.text_archetype')}: {archetype['archetype']}",
        distinction_text,
        translate(locale, "report.v2.comparison"),
        archetype["summary"],
        "",
        translate(locale, "report.v2.text_trait_scores"),
        f"{translate(locale, 'trait.aggression')}: {scores['aggression']:.0f}/100",
        f"{translate(locale, 'trait.precision')}: {scores['precision']:.0f}/100",
        f"{translate(locale, 'trait.utility')}: {scores['utility']:.0f}/100",
        f"{translate(locale, 'trait.positioning')}: {scores['positioning']:.0f}/100",
        "",
    ]
    lines.extend(common_text_lines(context))
    return "\n".join(lines), render_html_report_v2(context)
