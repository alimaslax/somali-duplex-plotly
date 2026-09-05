from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

import dash
import plotly.graph_objects as go
from dash import dcc, html

ROOT = Path(__file__).resolve().parent
AUDIT = [json.loads(line) for line in (ROOT / "data" / "speaker_audit.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
COLORS = {"ink": "#edf5f2", "muted": "#9aada8", "grid": "rgba(184,235,215,.13)", "cyan": "#79e2cf", "lime": "#c8ef79", "coral": "#ff9a73", "violet": "#a99bff"}


def group_name(item: dict) -> str:
    return item["file"].split("/", 1)[0]


def balance(item: dict) -> float:
    values = list(item["speaker_seconds"].values())
    return min(values) / max(values)


GROUPS: dict[str, list[dict]] = defaultdict(list)
for record in AUDIT:
    GROUPS[group_name(record)].append(record)


def style(figure: go.Figure, height: int = 390) -> go.Figure:
    figure.update_layout(height=height, margin={"l": 48, "r": 22, "t": 28, "b": 48}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"family": "Avenir Next, Avenir, sans-serif", "color": COLORS["muted"], "size": 12}, hoverlabel={"bgcolor": "#10201e", "font_color": COLORS["ink"], "bordercolor": COLORS["cyan"]}, showlegend=False)
    figure.update_xaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    figure.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    return figure


def collection_chart() -> go.Figure:
    names = list(GROUPS)
    hours = [sum(x["duration_seconds"] for x in GROUPS[name]) / 3600 for name in names]
    fig = go.Figure(go.Bar(x=names, y=[len(GROUPS[name]) for name in names], marker_color=[COLORS["cyan"], COLORS["lime"], COLORS["violet"]], customdata=hours, hovertemplate="%{x}<br>%{y} clips<br>%{customdata:.2f} raw WAV hours<extra></extra>"))
    fig.update_xaxes(title="Source collection")
    fig.update_yaxes(title="Accepted dual-speaker clips")
    return style(fig)


def balance_chart() -> go.Figure:
    values = [balance(x) for x in AUDIT]
    fig = go.Figure(go.Histogram(x=values, xbins={"start": 0, "end": 1, "size": .05}, marker={"color": COLORS["lime"], "line": {"width": 0}}, hovertemplate="Balance %{x:.2f}<br>%{y} clips<extra></extra>"))
    median = statistics.median(values)
    fig.add_vline(x=median, line_color=COLORS["coral"], line_width=2, line_dash="dot")
    fig.add_annotation(x=median, y=1, yref="paper", text=f"median {median:.2f}", showarrow=False, yshift=14, font={"color": COLORS["coral"], "size": 11})
    fig.update_xaxes(title="Minor-speaker seconds ÷ major-speaker seconds", range=[0, 1])
    fig.update_yaxes(title="Clips")
    return style(fig)


def evidence_chart() -> go.Figure:
    x = [list(item["speaker_seconds"].values())[0] for item in AUDIT]
    y = [list(item["speaker_seconds"].values())[1] for item in AUDIT]
    fig = go.Figure(go.Scattergl(x=x, y=y, mode="markers", marker={"color": COLORS["cyan"], "size": 7, "opacity": .55}, text=[x["file"] for x in AUDIT], hovertemplate="%{text}<br>speaker 00: %{x:.1f}s<br>speaker 01: %{y:.1f}s<extra></extra>"))
    fig.add_shape(type="line", x0=0, y0=0, x1=30, y1=30, line={"color": COLORS["coral"], "dash": "dot"})
    fig.update_xaxes(title="SPEAKER_00 seconds", range=[0, 32])
    fig.update_yaxes(title="SPEAKER_01 seconds", range=[0, 32], scaleanchor="x", scaleratio=1)
    return style(fig, 430)


def turns_chart() -> go.Figure:
    fig = go.Figure(go.Histogram(x=[sum(x["speaker_turns"].values()) for x in AUDIT], xbins={"start": 0, "end": 30, "size": 1}, marker={"color": COLORS["violet"], "line": {"width": 0}}, hovertemplate="%{x} turns<br>%{y} clips<extra></extra>"))
    fig.update_xaxes(title="Detected speaker turns per clip")
    fig.update_yaxes(title="Clips")
    return style(fig)


def model_chart() -> go.Figure:
    fig = go.Figure(go.Sankey(arrangement="snap", node={"label": ["IN", "STT", "LLM", "TTS", "OUT"], "pad": 28, "thickness": 20, "color": [COLORS["cyan"], COLORS["lime"], COLORS["violet"], COLORS["coral"], COLORS["cyan"]]}, link={"source": [0, 1, 2, 3], "target": [1, 2, 3, 4], "value": [10, 9, 8, 8], "color": ["rgba(121,226,207,.28)", "rgba(200,239,121,.28)", "rgba(169,155,255,.28)", "rgba(255,154,115,.28)"]}, hoverinfo="none"))
    fig.update_layout(height=255, margin={"l": 8, "r": 8, "t": 12, "b": 12}, paper_bgcolor="rgba(0,0,0,0)", font={"color": COLORS["ink"], "size": 12})
    return fig


def metric(label: str, value: str, detail: str) -> html.Div:
    return html.Div([html.Span(label), html.Strong(value), html.P(detail)], className="nemotron-metric")


def chart(title: str, detail: str, fig: go.Figure) -> html.Section:
    return html.Section([html.Div([html.H3(title), html.P(detail)], className="chart-copy"), dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})], className="nemotron-chart")


def layout() -> html.Main:
    total_hours = sum(x["duration_seconds"] for x in AUDIT) / 3600
    speaker_hours = sum(sum(x["speaker_seconds"].values()) for x in AUDIT) / 3600
    total_turns = sum(sum(x["speaker_turns"].values()) for x in AUDIT)
    samples = [("Ubax", "ubax-0053.wav", "42.4 sec · 25.3s / 17.5s speaker evidence"), ("Dhaxal", "dhaxal-0016.wav", "28.2 sec · 13.0s / 10.0s speaker evidence"), ("Qalbiga", "qalbiga-0135.wav", "29.0 sec · 14.7s / 11.8s speaker evidence")]
    return html.Main([
        html.Section([
            html.Div([html.Div("SOMALI DUPLEX / NEMOTRON VOICECHAT", className="signal-label"), html.H1(["Train toward ", html.Em("duplex"), " conversation—not just cleaner speech."]), html.P("This workspace follows the preparation path for a Somali conversational voice stack: auditable two-speaker WAV clips first, then transcripts, turn pairing, and model adaptation. It replaces the former speed-tier corpus story with evidence that matters for interruption-aware dialogue.", className="nemotron-lede"), html.Div([html.Span("24 kHz PCM WAV"), html.Span("exactly 2 speakers"), html.Span("629 accepted clips"), html.Span("speaker audit attached")], className="nemotron-tags")], className="nemotron-hero-copy"),
            html.Div([html.Div("MODEL PATH", className="signal-label"), dcc.Graph(figure=model_chart(), config={"displayModeBar": False, "responsive": True}), html.P(["NVIDIA's NeMo implementation describes Nemotron VoiceChat as an end-to-end duplex speech-to-speech model: a duplex STT model paired with an autoregressive speech decoder. ", html.A("Read the implementation", href="https://github.com/NVIDIA-NeMo/Speech/blob/main/nemo/collections/speechlm2/models/nemotron_voicechat.py", target="_blank")], className="architecture-note")], className="architecture-card")], className="nemotron-hero"),
        html.Section([metric("AUDITED CLIPS", f"{len(AUDIT):,}", "Every retained clip reports two speakers."), metric("RAW WAV TIME", f"{total_hours:.2f} h", "Mono, 24 kHz, 16-bit PCM."), metric("ATTRIBUTED SPEECH", f"{speaker_hours:.2f} h", "Sum of diarized speaker-time evidence."), metric("SPEAKER TURNS", f"{total_turns:,}", "Observed turn changes across accepted clips.")], className="nemotron-metrics"),
        html.Section([html.Div([html.Div("CORPUS EVIDENCE", className="signal-label"), html.H2("What the current dataset actually gives the model team."), html.P("The charts are computed from the filtered speaker_audit.jsonl—not inherited transcript speed labels.")], className="section-heading"), html.Div([chart("Collection coverage", "Accepted dual-speaker clips by source collection.", collection_chart()), chart("Speaker-time balance", "Near 1.0 means both speakers have similar attributed time.", balance_chart()), chart("Per-clip speaker evidence", "Each point is one candidate; the diagonal marks equal time.", evidence_chart()), chart("Turn density", "A view of conversational alternation rather than pace tiers.", turns_chart())], className="nemotron-chart-grid")], className="nemotron-section"),
        html.Section([html.Div([html.Div("WAV SPOT CHECKS", className="signal-label"), html.H2("Listen to the records behind the charts.")], className="section-heading"), html.Div([html.Figure([html.Figcaption([html.Strong(name), html.Span(detail)]), html.Audio(src=dash.get_asset_url(f"samples/{filename}"), controls=True, preload="metadata")], className="nemotron-audio") for name, filename, detail in samples], className="nemotron-audio-grid")], className="nemotron-section"),
        html.Section([html.Div([html.Div("TRAINING READINESS", className="signal-label"), html.H2("The next training gate is semantic alignment, not another audio-speed label.")], className="section-heading"), html.Div([html.Article([html.Span("01"), html.H3("Ready now"), html.P("Use the WAVs and diarization audit for acoustic inspection, clipping checks, speaker-balance sampling, and evaluation-fixture design.")]), html.Article([html.Span("02"), html.H3("Required before supervised duplex tuning"), html.P("Add reviewed Somali transcripts, speaker/turn order, and paired conversational context. This audit alone does not supply response targets.")]), html.Article([html.Span("03"), html.H3("Measure the model honestly"), html.P("Track streaming transcription, response quality, codec/audio quality, interruption behavior, latency, and Somali listener review on held-out conversations.")])], className="readiness-grid")], className="nemotron-section readiness-section"),
        html.Section([
            html.Div([html.Div("MODEL + TRAINING NOTE", className="signal-label"), html.H2("How a duplex turn moves through the stack."), html.P("Nemotron VoiceChat is designed for a conversation in motion: it listens to incoming audio while the dialogue state is still evolving, then produces the assistant response as generated speech rather than treating listening and speaking as unrelated batch jobs.")], className="section-heading"),
            html.Div([
                html.Article([html.H3("1. Listen and represent"), html.P("The streaming duplex STT path consumes a waveform and updates a text representation as speech arrives. For Somali work, this stage must be measured on held-out Somali conversations for transcription stability, endpoint timing, overlap behavior, and interruption recovery—not just word accuracy on isolated clips.")]),
                html.Article([html.H3("2. Decide the next turn"), html.P("The language layer uses the recognized conversational context to choose the assistant response. This is where turn order, role labels, transcript quality, and conversational intent matter. The current speaker audit has no response text targets, so it cannot by itself supervise this part of the model.")]),
                html.Article([html.H3("3. Speak in codec space"), html.P("The autoregressive EAR TTS path predicts audio-codec tokens for the answer and decodes them into a waveform. Audio quality work therefore needs both signal checks—sample rate, clipping, channel layout—and listener review for pronunciation, turn timing, naturalness, and unwanted overlap.")]),
            ], className="model-text-grid"),
            html.Div([
                html.Article([html.H3("What the 5.22 hours mean"), html.P("This build contains 629 accepted clips, totaling 5.22 raw WAV hours. It contains 3.47 attributed speaker-hours because diarization measures speech regions, not every second of the file. The difference is expected: pauses, silence, and non-attributed regions are not speaker training evidence.")]),
                html.Article([html.H3("What happens before tuning"), html.P("Create reviewed Somali transcripts, preserve which speaker owns each turn, and join adjacent turns into input → response examples. Split by source program before training so the same voices and episodes do not leak from training into evaluation. Keep the current audit as the acoustic eligibility record for every retained example.")]),
                html.Article([html.H3("What a credible experiment looks like"), html.P("Start with a fixed held-out conversational set and a baseline. Log streaming transcription quality, response quality, generated-audio quality, interruption handling, latency, and native Somali listener preference. Promote a checkpoint only when it improves the held-out suite—not when a training loss alone falls.")]),
            ], className="model-text-grid model-text-grid-secondary"),
        ], className="nemotron-section model-notes"),
        html.Footer("Somali Duplex · local WAV audit build · Nemotron / NeMo VoiceChat research dashboard", className="nemotron-footer"),
    ], className="nemotron-page")
