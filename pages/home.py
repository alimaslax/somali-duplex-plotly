import dash
from dash import html


dash.register_page(__name__, path="/", name="Home", title="Somali Duplex — Project Overview")


def tag(text: str) -> html.Span:
    return html.Span(text, className="tag")


def pipeline_step(number: str, title: str, detail: str, output: str) -> html.Article:
    return html.Article(
        [
            html.Div(number, className="step-number"),
            html.Div(
                [
                    html.H3(title),
                    html.P(detail),
                    html.Div([html.Span("OUTPUT"), output], className="step-output"),
                ],
                className="step-copy",
            ),
        ],
        className="pipeline-step",
    )


def principle(title: str, copy: str, label: str) -> html.Article:
    return html.Article(
        [html.Div(label, className="card-code"), html.H3(title), html.P(copy)],
        className="principle-card",
    )


def audio_clip(label: str, duration: str, audio_file: str, spectrogram_file: str) -> html.Figure:
    return html.Figure(
        [
            html.Figcaption(
                [
                    html.Div("GPT COMPARE", className="audio-eyebrow"),
                    html.Div([html.Strong(label), html.Span(duration)], className="audio-title-row"),
                ]
            ),
            html.Img(
                src=dash.get_asset_url(spectrogram_file),
                alt=f"Spectrogram for {label}",
                className="spectrogram",
            ),
            html.Audio(
                src=dash.get_asset_url(audio_file),
                controls=True,
                preload="metadata",
                className="comparison-audio",
            ),
        ],
        className="audio-clip",
    )


def layout(**kwargs) -> html.Main:
    return html.Main(
        [
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("SOMALI SPEECH · DATA TO VOICE", className="eyebrow"),
                            html.H1(["Teach the machine to ", html.Em("speak Somali"), " naturally."]),
                            html.Div(
                                [
                                    audio_clip("Segment A", "00:00–00:33", "gpt-compare-0-33.m4a", "gpt-compare-0-33-spectrogram.png"),
                                    audio_clip("Segment B", "00:33–00:54.97", "gpt-compare-33-end.m4a", "gpt-compare-33-end-spectrogram.png"),
                                ],
                                className="audio-comparison",
                            ),
                            html.P(
                                "Somali Duplex is an end-to-end research system for turning authorised native Somali recordings into a clean, reviewable corpus—and that corpus into a voice model that understands Somali pronunciation, rhythm, and prosody.",
                                className="hero-lede",
                            ),
                            html.Div(
                                [tag("Native Somali speech"), tag("24 kHz lossless audio"), tag("CosyVoice 3")],
                                className="tag-row",
                            ),
                        ],
                        className="hero-copy",
                    ),
                    html.Div(
                        [
                            html.Div("SIGNAL PATH", className="signal-label"),
                            html.Div(
                                [html.Span(style={"height": f"{height}px"}) for height in [18, 34, 54, 28, 66, 42, 76, 32, 58, 24, 48, 20, 38, 60, 30, 44]],
                                className="waveform",
                            ),
                            html.Div(
                                [
                                    html.Div([html.Strong("20–30 s"), html.Span("training clips")]),
                                    html.Div([html.Strong("24 kHz"), html.Span("target audio")]),
                                    html.Div([html.Strong("3 stages"), html.Span("model synthesis")]),
                                ],
                                className="signal-facts",
                            ),
                        ],
                        className="signal-card",
                    ),
                ],
                className="hero-grid",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("THE THESIS", className="eyebrow"),
                            html.H2("The language is the product."),
                        ],
                        className="section-heading",
                    ),
                    html.Div(
                        [
                            html.P(
                                "The objective is not English spoken with a Somali accent. The objective is written Somali rendered as fluent Somali speech: correct phonology, credible pauses, broadcaster-level clarity, and a voice that remains recognisably human.",
                                className="thesis-lede",
                            ),
                            html.P(
                                "A pretrained multilingual TTS system already knows how speech behaves. Somali Duplex concentrates the new learning on Somali text-to-speech mapping and Somali acoustics, backed by transcripts that match the recording rather than approximate it.",
                            ),
                        ],
                        className="thesis-copy",
                    ),
                ],
                className="content-section thesis-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("END-TO-END PIPELINE", className="eyebrow"),
                            html.H2("One chain of custody, from source to waveform."),
                            html.P(
                                "Every stage leaves a defined artifact. That makes quality measurable, failures traceable, and dataset versions reproducible.",
                                className="section-deck",
                            ),
                        ],
                        className="section-heading wide",
                    ),
                    html.Div(
                        [
                            pipeline_step("01", "Source responsibly", "Collect clear, long-form Somali speech only where recording and training rights are understood.", "Authorised raw recordings"),
                            pipeline_step("02", "Find speech", "Silero VAD locates speech and creates coherent 20–30 second learning units.", "Temporary speech segments"),
                            pipeline_step("03", "Clean the signal", "DeepFilterNet 3 removes background noise; loudness is normalised without keeping duplicate WAV intermediates.", "Mono 24 kHz, 16-bit FLAC"),
                            pipeline_step("04", "Transcribe precisely", "Somali text, word timestamps, speaker identity, and metadata are paired with every final clip.", "Audio–text pairs"),
                            pipeline_step("05", "Review the truth", "Label Studio supports human correction. Pause-aware punctuation is derived conservatively from real timing, never invented markup.", "Approved corpus version"),
                            pipeline_step("06", "Prepare the model", "Fixed train, development, and test splits become Kaldi-style manifests, embeddings, speech tokens, and Parquet shards.", "Training-ready dataset"),
                            pipeline_step("07", "Adapt and evaluate", "Fine-tune the language and acoustic stages, then gate promotion on Somali intelligibility, naturalness, identity, and waveform quality.", "Versioned Somali model bundle"),
                        ],
                        className="pipeline-list",
                    ),
                ],
                className="content-section pipeline-section",
            ),
            html.Section(
                [
                    html.Div("THE DATA CONTRACT", className="eyebrow"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Clean audio is necessary. Matched language is decisive."),
                                    html.P(
                                        "Each accepted clip is short enough to train, long enough to preserve phrasing, and paired with text that reflects what was actually spoken. Original recordings and derived transcripts remain separate; every transformation is auditable.",
                                    ),
                                ],
                                className="contract-copy",
                            ),
                            html.Div(
                                [
                                    html.Div([html.Span("AUDIO"), html.Strong("FLAC · mono · 24 kHz · 16-bit")]),
                                    html.Div([html.Span("TEXT"), html.Strong("Verified Somali transcript")]),
                                    html.Div([html.Span("IDENTITY"), html.Strong("Utterance + speaker IDs")]),
                                    html.Div([html.Span("PROVENANCE"), html.Strong("Source, version, audit trail")]),
                                ],
                                className="contract-spec",
                            ),
                        ],
                        className="contract-grid",
                    ),
                ],
                className="content-section contract-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("OPERATING PRINCIPLES", className="eyebrow"),
                            html.H2("Quality is protected at the boundaries."),
                        ],
                        className="section-heading wide",
                    ),
                    html.Div(
                        [
                            principle("Local-first processing", "VAD, denoising, and normalisation run locally. Final FLAC publication is separate from transcription and any external service.", "PROCESS"),
                            principle("Immutable source material", "Derived punctuation and training manifests are written into new versioned trees. Source audio and original transcripts stay intact.", "DATA"),
                            principle("A held-out truth set", "Train, development, and test splits are fixed before training, with source leakage prevented and speakers represented deliberately.", "EVAL"),
                            principle("Human ears decide", "Loss curves guide training; Somali listeners decide pronunciation, pacing, naturalness, and whether a checkpoint is ready.", "PROMOTION"),
                        ],
                        className="principles-grid",
                    ),
                ],
                className="content-section principles-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("MODEL STRATEGY", className="eyebrow"),
                            html.H2("Adapt meaning and acoustics. Preserve stable rendering."),
                            html.P(
                                "The first Somali experiment updates the CosyVoice 3 LLM and Flow model in separate full-parameter runs. HiFT remains frozen until evaluation proves the vocoder itself is the limiting factor.",
                                className="section-deck",
                            ),
                        ],
                        className="section-heading wide",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span("TEXT"), html.B("→"), html.Span("SPEECH TOKENS"), html.B("→"), html.Span("MEL"), html.B("→"), html.Span("WAVEFORM")], className="mini-route"),
                            html.A("Explore the CosyVoice 3 architecture →", href="/cosyvoice-3", className="text-link"),
                        ],
                        className="model-cta",
                    ),
                ],
                className="content-section model-section",
            ),
        ],
        className="page home-page reading-page",
    )
