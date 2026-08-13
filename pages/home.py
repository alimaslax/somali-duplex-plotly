import dash
from dash import html


dash.register_page(__name__, path="/", name="Overview", title="Somali Duplex — Research Notes")


def audio_clip(label: str, duration: str, audio_file: str, spectrogram_file: str) -> html.Figure:
    return html.Figure(
        [
            html.Figcaption([html.Strong(label), html.Span(duration)], className="audio-title-row"),
            html.Img(src=dash.get_asset_url(spectrogram_file), alt=f"Spectrogram for {label}", className="spectrogram"),
            html.Audio(src=dash.get_asset_url(audio_file), controls=True, preload="metadata", className="comparison-audio"),
        ],
        className="audio-clip",
    )


def pipeline_row(stage: str, action: str, artifact: str) -> html.Tr:
    return html.Tr([html.Th(stage, scope="row"), html.Td(action), html.Td(artifact)])


def layout(**kwargs) -> html.Main:
    return html.Main(
        html.Article(
            [
                html.Header(
                    [
                        html.H1("Somali Duplex: Building a Reviewable Somali Speech Corpus for Natural Voice Synthesis"),
                        html.A("[ Research code ]", href="/cosyvoice-3", className="paper-code-link"),
                        html.P("Somali Duplex Research", className="paper-authors"),
                        html.P(
                            [html.Strong("Abstract: "), "Somali Duplex is a local-first workflow for turning authorised native Somali recordings into a clean, reviewable speech corpus and adapting a text-to-speech model from it. The work prioritises faithful transcripts, inspectable audio processing, controlled dataset versions, and listener-led evaluation of pronunciation, rhythm, and naturalness."],
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
                                html.Li(html.A("1. Reference audio", href="#reference-audio")),
                                html.Li(html.A("2. Research objective", href="#objective")),
                                html.Li(html.A("3. Corpus method", href="#method")),
                                html.Li(html.A("4. Dataset contract", href="#dataset-contract")),
                                html.Li(html.A("5. Operating assumptions", href="#assumptions")),
                            ]
                        ),
                    ],
                    className="paper-contents",
                ),
                html.Section(
                    [
                        html.H2("1. Reference audio"),
                        html.Blockquote(
                            "Warbixinno ka soo baxay dowladda UK ayaa sheegaya in, haddii carqaladaynta maraakiibta ee marinka Hormuz ay sii socoto illaa dhammaadka sanadkan, dhaqaalaha Britain uu sannadka dambe yeelan doono koboc aad u yar ama ku dhowaad aan wax koboc ah lahayn. Saraakiisha Wasaaradda Maaliyadda Ingiriiska ayaa arrintan ku sheegay warbixin loo gudbiyay Ra’iisul Wasaaraha. Sida laga soo xigtay ilo ka tirsan dowladda, qaab-dhismeedka saadaasha gudaha ee Wasaaradda Maaliyadda ayaa muujinaya in koboca wax-soo-saarka guud ee dalka, GDP-ga UK, uu hoos u dhici karo ilaa eber dhibic saddex boqolkiiba sannadka laba kun iyo toddoba iyo labaatan. Saraakiisha dowladda ayaa sheegay inay si joogto ah ugu diyaar garoobaan dhammaan xaaladaha suurtagalka ah, ayna tilmaameen in saadaashan koboca ay ku salaysan tahay xaalad ka sii xun tan hadda jirta. Warbixintan ayaa soo baxday xilli dhaqaalaha Britain uu horeyba u wajahayo koboc xaddidan. Xafiiska Tirakoobka Qaranka ee UK ayaa la filayaa inuu dhowaan ku dhawaaqo in wax-soo-saarka guud ee dalka, GDP-ga, uusan wax koboc ah samayn bishii Juun.",
                            className="reference-audio-quote",
                        ),
                        html.Div(
                            [
                                audio_clip("00:09–00:53", "44 seconds", "gpt-compare-0-33.m4a", "gpt-compare-0-33-spectrogram.png"),
                                audio_clip("01:25–02:11", "46 seconds", "gpt-compare-33-end.m4a", "gpt-compare-33-end-spectrogram.png"),
                            ],
                            className="audio-comparison",
                        ),
                    ],
                    id="reference-audio",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("2. Research objective"),
                        html.P("The goal is written Somali rendered as fluent Somali speech: accurate pronunciation, believable phrase breaks, clear delivery, and a voice that remains recognisably human.", className="key-statement"),
                        html.P("A multilingual TTS model already contains a broad model of speech. This project focuses its new learning on Somali text-to-speech correspondence and Somali acoustics, using transcripts that describe what was actually recorded."),
                    ],
                    id="objective",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("3. Corpus method"),
                        html.P("Each stage produces a named artifact. That keeps the corpus inspectable and makes training failures traceable."),
                        html.Div(
                            html.Table(
                                [
                                    html.Thead(html.Tr([html.Th("Stage"), html.Th("Work"), html.Th("Artifact")])),
                                    html.Tbody(
                                        [
                                            pipeline_row("Source", "Collect authorised long-form Somali recordings.", "Raw recording"),
                                            pipeline_row("Segment", "Use VAD to find coherent 20–30 second speech units.", "Temporary speech clips"),
                                            pipeline_row("Publish", "Denoise and normalise locally; publish mono 24 kHz FLAC.", "Final audio"),
                                            pipeline_row("Transcribe", "Pair every clip with verified Somali text and metadata.", "Audio–text record"),
                                            pipeline_row("Review", "Correct text and derive punctuation only from evidence.", "Approved corpus version"),
                                            pipeline_row("Train", "Prepare fixed splits, manifests, tokens, and shards.", "Training dataset"),
                                            pipeline_row("Evaluate", "Adapt LLM and Flow; promote only after listener review.", "Versioned model bundle"),
                                        ]
                                    ),
                                ],
                                className="method-table",
                            ),
                            className="table-scroll",
                        ),
                    ],
                    id="method",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("4. Dataset contract"),
                        html.Dl(
                            [
                                html.Div([html.Dt("Audio"), html.Dd("Mono FLAC · 24 kHz · 16-bit")]),
                                html.Div([html.Dt("Text"), html.Dd("Verified Somali transcript")]),
                                html.Div([html.Dt("Identity"), html.Dd("Utterance and speaker IDs")]),
                                html.Div([html.Dt("Provenance"), html.Dd("Source, version, and audit trail")]),
                            ],
                            className="research-definition-list",
                        ),
                    ],
                    id="dataset-contract",
                    className="research-section",
                ),
                html.Section(
                    [
                        html.H2("5. Operating assumptions"),
                        html.Ul(
                            [
                                html.Li("Audio processing is local-first; publication is separate from transcription or external services."),
                                html.Li("Source material is preserved; derived transcripts and manifests are versioned separately."),
                                html.Li("Train, development, and test splits are fixed before training and protected from source leakage."),
                                html.Li("Loss curves inform the work; Somali listeners determine whether a checkpoint is ready."),
                            ],
                            className="research-list",
                        ),
                    ],
                    id="assumptions",
                    className="research-section",
                ),
            ],
            className="research-paper",
        ),
        className="page home-page research-document",
    )
