"""Plotly chart builders used by the HTML report."""

import plotly.graph_objects as go

from ..localization import translate


def render_velocity_chart(
    velocity_75_100: int,
    velocity_100_150: int,
    velocity_over_150: int,
    locale: str = "en",
) -> str:
    """Create the moving rifle shot velocity distribution chart."""
    chart = go.Figure(
        data=[
            go.Bar(
                x=["75\u2013100", "100\u2013150", ">150"],
                y=[velocity_75_100, velocity_100_150, velocity_over_150],
                marker_color=["#60a5fa", "#818cf8", "#fb7185"],
                text=[velocity_75_100, velocity_100_150, velocity_over_150],
                textposition="outside",
                hovertemplate=translate(locale, "chart.velocity_hover"),
            )
        ]
    )
    chart.update_layout(
        title=translate(locale, "chart.velocity_title"),
        xaxis_title=translate(locale, "chart.velocity_axis"),
        yaxis_title=translate(locale, "chart.shot_count"),
        yaxis=dict(rangemode="tozero", dtick=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#1f2937"),
        margin=dict(l=50, r=24, t=60, b=55),
        height=380,
    )
    return chart.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
    )
