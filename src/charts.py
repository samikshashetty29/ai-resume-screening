"""Plotly charts for the results dashboard."""

import plotly.graph_objects as go

from src.skill_extractor import category_of

MATCHED_COLOR = "#2e9e5b"
MISSING_COLOR = "#e0a030"


def score_gauge(value, title: str) -> go.Figure:
    """A 0-100 gauge. value=None shows an empty gauge marked 'n/a'."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value if value is not None else 0,
        number={"suffix": "%", "valueformat": ".1f"} if value is not None
               else {"suffix": " n/a", "font": {"color": "#999"}, "valueformat": ".0f"},
        title={"text": title, "font": {"size": 15}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#4a6fd1"},
            "steps": [
                {"range": [0, 33], "color": "rgba(128,128,128,0.10)"},
                {"range": [33, 66], "color": "rgba(128,128,128,0.18)"},
                {"range": [66, 100], "color": "rgba(128,128,128,0.26)"},
            ],
        },
    ))
    fig.update_layout(height=220, margin=dict(l=25, r=25, t=50, b=10))
    return fig


def top_keywords_chart(keywords) -> go.Figure:
    """Horizontal bars of (term, points), biggest at the top."""
    terms = [term for term, _ in keywords]
    points = [value for _, value in keywords]
    fig = go.Figure(go.Bar(
        x=points, y=terms, orientation="h", marker_color="#4a6fd1",
        text=[f"{value:.1f}" for value in points], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f} points of the score<extra></extra>",
    ))
    fig.update_layout(
        title={"text": "Shared words adding most to the text similarity score", "font": {"size": 15}},
        xaxis_title="Points of the similarity score",
        yaxis={"autorange": "reversed"},
        height=110 + 32 * len(terms),
        margin=dict(l=10, r=40, t=50, b=40),
    )
    return fig


def skills_by_category_chart(matched, missing) -> go.Figure:
    """Stacked horizontal bars: matched vs not-detected job skills per category."""
    categories = sorted({category_of(s) for s in list(matched) + list(missing)})
    matched_counts = [sum(category_of(s) == c for s in matched) for c in categories]
    missing_counts = [sum(category_of(s) == c for s in missing) for c in categories]
    matched_names = ["<br>".join(s for s in matched if category_of(s) == c) for c in categories]
    missing_names = ["<br>".join(s for s in missing if category_of(s) == c) for c in categories]

    fig = go.Figure([
        go.Bar(name="Matched", y=categories, x=matched_counts, orientation="h",
               marker_color=MATCHED_COLOR, customdata=matched_names,
               hovertemplate="%{y}: %{x} matched<br>%{customdata}<extra></extra>"),
        go.Bar(name="Not detected", y=categories, x=missing_counts, orientation="h",
               marker_color=MISSING_COLOR, customdata=missing_names,
               hovertemplate="%{y}: %{x} not detected<br>%{customdata}<extra></extra>"),
    ])
    fig.update_layout(
        barmode="stack",
        title={"text": "Job skills by category", "font": {"size": 15}},
        xaxis_title="Number of job skills",
        xaxis={"dtick": 1},
        height=120 + 45 * len(categories),
        margin=dict(l=10, r=10, t=50, b=40),
        legend=dict(orientation="h", y=-0.25 if len(categories) > 2 else -0.6),
    )
    return fig
