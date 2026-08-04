import dash
from dash import html


dash.register_page(
    __name__,
    path="/cosyvoice-3",
    name="CosyVoice 3",
    title="Somali Duplex — CosyVoice 3",
)


def module_row(stage: str, function: str, Somali_plan: str) -> html.Tr:
    return html.Tr(
        [html.Th(stage, scope="row"), html.Td(function), html.Td(Somali_plan)]
    )


def layout(**kwargs) -> html.Main:
    return html.Main(
        html.Article(
            [
                html.Header(
                    [
                        html.H1("CosyVoice 3: a practical model note for Somali voice synthesis"),
                        html.P("Somali Duplex Research", className="paper-authors"),
                        html.P(
                            [
                                html.Strong("Abstract: "),
                                "CosyVoice 3 synthesizes speech in three steps: it plans discrete speech tokens from text, converts those tokens into acoustic features, and renders a waveform. Somali Duplex adapts the language and acoustic stages using a reviewed Somali corpus while preserving the base waveform renderer for the first experiments.",
                            ],
                            className="paper-abstract",
                        ),
                    ],
                    className="paper-title-block",
                ),
                html.Nav(
                    [
                        html.H2("Contents"),
                        html.Ul(
                            [
                                html.Li(html.A("1. Model scope", href="#model-scope")),
                                html.Li(html.A("2. Conditioning inputs", href="#conditioning")),
                                html.Li(html.A("3. Checkpoint roles", href="#checkpoints")),
                                html.Li(html.A("4. Training and evaluation", href="#training")),
                            ]
                        ),
                    ],
                    className="paper-contents",
                ),
                html.Section(
                    [
                        html.H2("1. Model scope"),
                        html.P(
                            "CosyVoice 3 does not generate audio directly from Somali text. The model first decides on a sequence of speech tokens, then turns that sequence into a mel-spectrogram, and finally renders the mel representation as a 24 kHz waveform. Treating these as separate stages makes model errors easier to locate and evaluate."
                        ),
                        html.P(
                            "The first Somali adaptation is deliberately narrow: update the stages responsible for pronunciation, timing, and acoustics, while keeping the established waveform renderer fixed."
                        ),
                    ],
                    id="model-scope",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("2. Conditioning inputs"),
                        html.P(
                            "Before generation, the frontend prepares the requested Somali text and reference prompt into compatible conditioning signals. These are inputs to the model, not additional trainable stages."
                        ),
                        html.Div(
                            html.Table(
                                [
                                    html.Thead(html.Tr([html.Th("Input"), html.Th("Role")])),
                                    html.Tbody(
                                        [
                                            html.Tr([html.Th("Text tokens", scope="row"), html.Td("The existing Qwen2 tokenizer encodes Somali spelling without a custom language tag.")]),
                                            html.Tr([html.Th("Prompt speech tokens", scope="row"), html.Td("A Whisper-style prompt representation supplies reference acoustic context.")]),
                                            html.Tr([html.Th("Speaker embedding", scope="row"), html.Td("CampPlus supplies a compact representation of the reference speaker identity.")]),
                                            html.Tr([html.Th("Prompt mel", scope="row"), html.Td("An 80-bin, 24 kHz mel-spectrogram preserves local acoustic context for Flow.")]),
                                        ]
                                    ),
                                ],
                                className="method-table",
                            ),
                            className="table-scroll",
                        ),
                    ],
                    id="conditioning",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("3. Checkpoint roles"),
                        html.P("Each checkpoint has a distinct responsibility. The training plan changes only the stages where Somali evidence is expected to improve the output."),
                        html.Div(
                            html.Table(
                                [
                                    html.Thead(html.Tr([html.Th("Stage"), html.Th("Function"), html.Th("First Somali plan")])),
                                    html.Tbody(
                                        [
                                            module_row("LLM", "Somali text → discrete speech tokens", "Fine-tune fully for pronunciation, phrase timing, and prosodic intent."),
                                            module_row("Flow", "Speech tokens + prompt context → 80-bin mel", "Fine-tune fully for Somali acoustics, rhythm, and voice realization."),
                                            module_row("HiFT", "Mel + predicted pitch → 24 kHz waveform", "Keep frozen initially as the stable waveform renderer."),
                                        ]
                                    ),
                                ],
                                className="method-table",
                            ),
                            className="table-scroll",
                        ),
                    ],
                    id="checkpoints",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("4. Training and evaluation"),
                        html.P(
                            "LLM and Flow experiments run independently before their combined run, so each adaptation can be measured against the base model. A promoted Somali bundle replaces only llm.pt and flow.pt; hift.pt remains unchanged unless waveform artifacts persist after the upstream stages are demonstrably stable."
                        ),
                        html.Ul(
                            [
                                html.Li("Use fixed train, development, and held-out test splits with no source leakage."),
                                html.Li("Compare Somali intelligibility, pronunciation, pacing, naturalness, speaker similarity, and waveform quality."),
                                html.Li("Promote a checkpoint only after native Somali listener review confirms an improvement."),
                            ],
                            className="research-list",
                        ),
                    ],
                    id="training",
                    className="research-section",
                ),
            ],
            className="research-paper cosyvoice-paper",
        ),
        className="page cosyvoice-page cosyvoice-paper-document",
    )
