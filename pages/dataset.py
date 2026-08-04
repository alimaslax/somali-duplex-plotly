from __future__ import annotations

import json
from pathlib import Path

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html


dash.register_page(
    __name__,
    path="/dataset",
    name="Dataset",
    title="Somali Duplex — Omar Dataset",
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ROOT / "data" / "omar_dataset_summary.json").read_text(encoding="utf-8"))
CLIPS = pd.read_csv(ROOT / "data" / "omar_wpm.csv")

COLORS = {
    "Low": "#53b7c7",
    "Medium": "#8d97a5",
    "High": "#f2a35f",
    "Outlier": "#ef6868",
    "ink": "#c9d4dc",
    "muted": "#8094a0",
    "grid": "rgba(135, 157, 170, 0.15)",
}


def base_figure(figure: go.Figure, height: int = 430) -> go.Figure:
    figure.update_layout(
        height=height,
        margin={"l": 48, "r": 24, "t": 24, "b": 46},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Avenir Next, Avenir, sans-serif", "color": COLORS["muted"], "size": 12},
        hoverlabel={"bgcolor": "#1d262c", "font_color": "#f1f5f7", "bordercolor": "#526976"},
        showlegend=False,
    )
    figure.update_xaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    figure.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    return figure


def wpm_distribution() -> go.Figure:
    rates = SUMMARY["speaking_rate"]
    low = rates["low_boundary_wpm"]
    high = rates["high_boundary_wpm"]
    figure = go.Figure(
        go.Histogram(
            x=CLIPS["wpm"],
            xbins={"start": 0, "end": 250, "size": 5},
            marker={"color": "#6b91a5", "line": {"width": 0}},
            opacity=0.92,
            hovertemplate="%{x:.0f} WPM bin<br>%{y:,} clips<extra></extra>",
        )
    )
    figure.add_vrect(x0=0, x1=low, fillcolor=COLORS["Low"], opacity=0.09, line_width=0)
    figure.add_vrect(x0=low, x1=high, fillcolor=COLORS["Medium"], opacity=0.08, line_width=0)
    figure.add_vrect(x0=high, x1=250, fillcolor=COLORS["High"], opacity=0.09, line_width=0)
    for boundary, label, color, anchor in ((low, "LOW", COLORS["Low"], "right"), (high, "HIGH", COLORS["High"], "left")):
        figure.add_vline(x=boundary, line_width=1.5, line_dash="dot", line_color=color)
        figure.add_annotation(
            x=boundary,
            y=1,
            yref="paper",
            text=label,
            showarrow=False,
            yshift=16,
            xanchor=anchor,
            font={"family": "SFMono-Regular, Consolas, monospace", "size": 10, "color": color},
        )
    figure.update_xaxes(title="Overall speaking rate (words per minute)", range=[0, 250], dtick=25)
    figure.update_yaxes(title="Clips")
    return base_figure(figure, 470)


def duration_scatter() -> go.Figure:
    figure = go.Figure()
    for tier in ("Low", "Medium", "High"):
        subset = CLIPS[CLIPS["wpm_tier"] == tier]
        figure.add_trace(
            go.Scattergl(
                x=subset["duration_seconds"],
                y=subset["wpm"],
                mode="markers",
                name=tier,
                marker={"size": 5, "color": COLORS[tier], "opacity": 0.42},
                customdata=subset[["word_count", "recording", "utterance"]],
                hovertemplate=(
                    f"{tier} · %{{y:.1f}} WPM<br>"
                    "%{x:.1f} sec · %{customdata[0]} words<br>"
                    "%{customdata[1]} / %{customdata[2]}<extra></extra>"
                ),
            )
        )
    figure.add_vrect(x0=20, x1=30, fillcolor="#70a7b8", opacity=0.07, line_width=0)
    figure.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.08, "x": 0})
    figure.update_xaxes(title="Clip duration (seconds)")
    figure.update_yaxes(title="Words per minute", range=[0, 260])
    return base_figure(figure, 420)


def source_boxplot() -> go.Figure:
    recordings = [item["recording"] for item in SUMMARY["top_recordings_by_hours"][:10]]
    figure = go.Figure()
    for index, recording in enumerate(recordings):
        values = CLIPS.loc[CLIPS["recording"] == recording, "wpm"]
        short_name = recording[:42] + ("…" if len(recording) > 42 else "")
        figure.add_trace(
            go.Box(
                x=values,
                name=short_name,
                orientation="h",
                boxpoints=False,
                line={"color": COLORS["Low"] if index % 2 == 0 else COLORS["High"], "width": 1.2},
                fillcolor="rgba(104, 145, 163, 0.12)",
                hovertemplate="%{x:.1f} WPM<extra>%{y}</extra>",
            )
        )
    figure.update_xaxes(title="Words per minute", range=[40, 220])
    figure.update_yaxes(autorange="reversed", tickfont={"size": 10})
    return base_figure(figure, 520)


def metric(label: str, value: str, note: str) -> html.Div:
    return html.Div(
        [html.Span(label, className="dataset-metric-label"), html.Strong(value), html.P(note)],
        className="dataset-metric",
    )


def tier_card(tier: dict[str, object], instruction: str) -> html.Article:
    name = str(tier["tier"])
    return html.Article(
        [
            html.Div([html.Span(name), html.B(f"{tier['clips']:,} clips")], className="tier-card-header"),
            html.Strong(f"{tier['median_wpm']:.1f} WPM", className="tier-rate"),
            html.P(f"Observed range {tier['min_wpm']:.1f}–{tier['max_wpm']:.1f} WPM · {tier['hours']:.1f} hours"),
            html.Code(instruction),
        ],
        className=f"tier-card tier-{name.lower()}",
    )


def finding(number: str, title: str, text: str) -> html.Div:
    return html.Div(
        [html.Span(number), html.Div([html.H3(title), html.P(text)])],
        className="dataset-finding",
    )


def normalization_step(stage: str, title: str, detail: str, evidence: str) -> html.Div:
    return html.Div(
        [
            html.Span(stage, className="normalization-stage"),
            html.Div([html.H3(title), html.P(detail)]),
            html.Code(evidence),
        ],
        className="normalization-step",
    )


def recordings_table() -> html.Div:
    rows = SUMMARY["top_recordings_by_hours"][:10]
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th("Recording"), html.Th("Clips"), html.Th("Hours"), html.Th("Median WPM")])),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(item["recording"]),
                                html.Td(f"{item['clips']:,}"),
                                html.Td(f"{item['hours']:.2f}"),
                                html.Td(f"{item['median_wpm']:.1f}"),
                            ]
                        )
                        for item in rows
                    ]
                ),
            ],
            className="dataset-table",
        ),
        className="dataset-table-wrap",
    )


def layout(**kwargs) -> html.Main:
    corpus = SUMMARY["corpus"]
    rates = SUMMARY["speaking_rate"]
    pauses = SUMMARY["pauses"]
    audio = SUMMARY["audio"]
    punctuation = SUMMARY["punctuation_normalization"]
    tiers = {tier["tier"]: tier for tier in SUMMARY["tiers"]}
    total_insertions = punctuation["total_proposed_commas"] + punctuation["total_proposed_periods"]

    return html.Main(
        [
            html.Header(
                [
                    html.Div("DATASET / OMAR / FULL TRANSCRIPT SCAN", className="eyebrow"),
                    html.H1(["How fast does Omar ", html.Em("actually"), " speak?"]),
                    html.P(
                        f"Every one of the {corpus['json_files_discovered']:,} transcript JSON files was inspected. "
                        "The result is a data-derived pace vocabulary for instruction training—not a guessed threshold.",
                        className="dataset-hero-copy",
                    ),
                    html.Div(
                        [
                            metric("CORPUS TIME", f"{corpus['total_hours']:.2f} h", f"{corpus['valid_clips']:,} timed clips"),
                            metric("TIMED WORDS", f"{corpus['total_words']:,}", "type = word only"),
                            metric("MEDIAN PACE", f"{rates['median_wpm']:.1f}", "overall WPM"),
                            metric("SOURCE RECORDINGS", f"{corpus['recording_sources']:,}", "distinct recording folders"),
                        ],
                        className="dataset-metrics",
                    ),
                ],
                className="dataset-hero",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("PACE DISTRIBUTION", className="eyebrow"),
                            html.H2("The middle half lives between 120.9 and 154.5 WPM."),
                            html.P(
                                "Overall WPM includes silence and hesitation, so it represents the pace a listener experiences. "
                                "The bands use the corpus quartiles: the bottom quarter is Low, the middle half is Medium, and the top quarter is High.",
                            ),
                        ],
                        className="dataset-section-heading",
                    ),
                    html.Div(
                        dcc.Graph(figure=wpm_distribution(), config={"displayModeBar": False, "responsive": True}),
                        className="dataset-chart signature-chart",
                    ),
                    html.Div(
                        [
                            tier_card(tiers["Low"], "Speak slowly and deliberately."),
                            tier_card(tiers["Medium"], "Speak at a natural, moderate pace."),
                            tier_card(tiers["High"], "Speak at a fast pace."),
                        ],
                        className="tier-grid",
                    ),
                    html.Div(
                        [
                            html.Strong("Recommended labeling rule"),
                            html.P(
                                f"Low < {rates['low_boundary_wpm']:.1f} WPM · Medium {rates['low_boundary_wpm']:.1f}–{rates['high_boundary_wpm']:.1f} WPM · High > {rates['high_boundary_wpm']:.1f} WPM. "
                                f"Keep the {rates['outlier_clips']} Tukey outliers in a review bucket instead of teaching the model that transcript failures mean “speak slowly.”"
                            ),
                        ],
                        className="dataset-recommendation",
                    ),
                ],
                className="dataset-section",
            ),
            html.Section(
                [
                    html.Div("CLIP GEOMETRY", className="eyebrow"),
                    html.H2("Duration is controlled; delivery is not uniform."),
                    html.P(
                        f"{corpus['clips_20_to_30_percentage']:.2f}% of valid clips are inside the intended 20–30 second window. "
                        "The scatter exposes the short, long, sparse, and unusually dense clips that should be reviewed before automatic instruction labeling.",
                        className="dataset-section-deck",
                    ),
                    html.Div(
                        dcc.Graph(figure=duration_scatter(), config={"displayModeBar": False, "responsive": True}),
                        className="dataset-chart",
                    ),
                ],
                className="dataset-section dataset-geometry-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("WHAT THE SCAN FOUND", className="eyebrow"),
                            html.H2("Six decisions fall out of the numbers."),
                        ],
                        className="dataset-section-heading",
                    ),
                    html.Div(
                        [
                            finding("01", f"The corpus is {corpus['total_hours']:.2f} hours—not approximately 100.", f"All JSON durations total {corpus['total_hours']:.2f} hours. {corpus['wpm_eligible_hours']:.2f} hours have usable timed words; three audio-event-only clips are retained in the corpus inventory but excluded from pace labels."),
                            finding("02", "Omar’s experienced pace centers at 137.7 WPM.", f"The mean is {rates['mean_wpm']:.1f} WPM and the median is {rates['median_wpm']:.1f}; their closeness means the central distribution is balanced enough for quartile bands."),
                            finding("03", "Articulation is much faster than overall tempo.", f"Median articulation rate is {rates['median_articulation_wpm']:.1f} WPM after removing timestamp gaps. Omar often speaks in quick runs separated by pauses."),
                            finding("04", "The tails contain real review work.", f"There are {rates['outlier_clips']} WPM outliers outside {rates['lower_outlier_fence_wpm']:.1f}–{rates['upper_outlier_fence_wpm']:.1f} WPM, plus {corpus['invalid_clips']} JSON files with no usable timed words."),
                            finding("05", "The audio contract is fully consistent.", f"All {audio['audio_files_scanned']:,} matched files are mono, 24 kHz, PCM-16 FLAC. JSON and FLAC durations agree to {audio['max_json_audio_duration_delta_seconds']:.4f} seconds."),
                            finding("06", "Pause evidence is abundant.", f"Median inter-word gap is {pauses['median_interword_gap_seconds']:.2f}s, but {pauses['gaps_at_least_0_75']:,} gaps reach 0.75s and {pauses['gaps_at_least_1_40']:,} reach 1.40s—enough evidence to study both pace and punctuation."),
                        ],
                        className="dataset-findings",
                    ),
                ],
                className="dataset-section findings-section",
            ),
            html.Section(
                [
                    html.Div("NORMALIZATION RECORD", className="eyebrow"),
                    html.H2("What was standardized—and what was preserved."),
                    html.P(
                        "Normalization makes clips technically comparable without flattening the timing evidence needed for prosody research.",
                        className="dataset-section-deck",
                    ),
                    html.Div(
                        [
                            normalization_step("AUDIO 01", "Segment", "Silero VAD targets 20–30 second speech clips. Completed source folders are reused and conflicting partial output is rejected.", f"{corpus['clips_20_to_30_percentage']:.2f}% in target window"),
                            normalization_step("AUDIO 02", "Clean", "DeepFilterNet 3 denoises each segment, then loudness normalization reduces recording-level gain differences.", "model loaded once per batch"),
                            normalization_step("AUDIO 03", "Publish", "Final files are lossless mono FLAC at 24 kHz and 16-bit PCM. Temporary VAD WAV files are discarded.", f"{audio['audio_files_scanned']:,}/{audio['matching_flac_files']:,} verified"),
                            normalization_step("TEXT 01", "Align", "Timed lexical words are compared with the canonical transcript before punctuation is proposed. Word mismatches become review flags.", f"{punctuation['source_json_count']:,} JSON/TXT pairs"),
                            normalization_step("TEXT 02", "Punctuate", "Gaps from 0.30s propose commas; gaps from 0.75s propose periods. The source JSON and original transcript remain unchanged.", f"{total_insertions:,} proposed marks"),
                            normalization_step("TEXT 03", "Audit", "The derived transcript tree records every edit and review reason. It does not introduce pause tags, SSML, or invented Somali words.", f"{punctuation['review_manifest_count']:,} review records"),
                        ],
                        className="normalization-ledger",
                    ),
                ],
                className="dataset-section normalization-section",
            ),
            html.Section(
                [
                    html.Div("SOURCE VARIATION", className="eyebrow"),
                    html.H2("The biggest recordings do not share one pace."),
                    html.P("Each box shows the WPM spread within one of the ten largest recording folders. This is why thresholds should be corpus-derived, then reviewed at clip level.", className="dataset-section-deck"),
                    html.Div(
                        dcc.Graph(figure=source_boxplot(), config={"displayModeBar": False, "responsive": True}),
                        className="dataset-chart source-chart",
                    ),
                    recordings_table(),
                ],
                className="dataset-section source-section",
            ),
            html.Footer(
                [
                    html.Div("REPRODUCIBILITY", className="eyebrow"),
                    html.P("Generated by scripts/analyze_omar_dataset.py from every processed/omar/*/transcripts/*.json file. The page reads the checked analysis artifacts in data/omar_wpm.csv and data/omar_dataset_summary.json."),
                ],
                className="dataset-footer",
            ),
        ],
        className="dataset-page",
    )
