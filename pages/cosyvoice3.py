import dash
from dash import html


dash.register_page(
    __name__,
    path="/cosyvoice-3",
    name="CosyVoice 3",
    title="Somali Duplex — CosyVoice 3 Architecture",
)


def spec(label: str, value: str) -> html.Div:
    return html.Div([html.Span(label), html.Strong(value)], className="spec-row")


def architecture_stage(number: str, title: str, role: str, status: str, class_name: str) -> html.Article:
    return html.Article(
        [
            html.Div(number, className="architecture-number"),
            html.Div([html.H3(title), html.P(role)], className="architecture-copy"),
            html.Span(status, className="architecture-status"),
        ],
        className=f"architecture-stage {class_name}",
    )


def layout(**kwargs) -> html.Main:
    return html.Main(
        [
            html.Section(
                [
                    html.Div("COSYVOICE 3 · MODEL ARCHITECTURE", className="eyebrow"),
                    html.H1(["Text becomes voice through ", html.Em("three representations"), "."]),
                    html.P(
                        "CosyVoice 3 does not predict a waveform directly from text. It first plans speech as discrete tokens, expands those tokens into an acoustic mel-spectrogram, then renders that spectrogram as a 24 kHz waveform. Somali Duplex adapts the first two transformations and initially freezes the third.",
                        className="hero-lede architecture-lede",
                    ),
                ],
                className="architecture-hero",
            ),
            html.Section(
                [
                    html.Div("INFERENCE ROUTE", className="eyebrow"),
                    html.Div(
                        [
                            architecture_stage("01", "LLM", "Somali text → discrete speech tokens", "FULL FINE-TUNE", "llm-stage"),
                            html.Div("↓", className="route-arrow"),
                            architecture_stage("02", "Flow", "Speech tokens + speaker condition → mel", "FULL FINE-TUNE", "flow-stage"),
                            html.Div("↓", className="route-arrow"),
                            architecture_stage("03", "HiFT", "Mel + predicted pitch → 24 kHz waveform", "FROZEN FIRST", "hift-stage"),
                        ],
                        className="architecture-route",
                    ),
                ],
                className="content-section route-section",
            ),
            html.Section(
                [
                    html.Div(
                        [html.Div("BEFORE THE THREE STAGES", className="eyebrow"), html.H2("The frontend builds the conditioning context.")],
                        className="section-heading wide",
                    ),
                    html.P(
                        "The frontend is not one of the three checkpoint stages, but it determines what they receive. For zero-shot synthesis, it reads the requested text and a prompt recording, then creates four complementary views of that prompt.",
                        className="section-deck frontend-deck",
                    ),
                    html.Div(
                        [
                            html.Article([html.Div("T", className="input-glyph"), html.H3("Qwen2 text tokens"), html.P("The CosyVoice-BlankEN BPE tokenizer encodes Somali spelling losslessly. No custom <|so|> language tag is needed or supported.")], className="input-card"),
                            html.Article([html.Div("S", className="input-glyph"), html.H3("V3 speech tokens"), html.P("A Whisper-style log-mel view of the prompt enters speech_tokenizer_v3.onnx, producing the acoustic token sequence used as reference context.")], className="input-card"),
                            html.Article([html.Div("V", className="input-glyph"), html.H3("CampPlus identity"), html.P("An 80-bin filterbank enters CampPlus and returns a 192-dimensional speaker embedding that conditions voice identity.")], className="input-card"),
                            html.Article([html.Div("M", className="input-glyph"), html.H3("Prompt mel"), html.P("The prompt is also resampled to 24 kHz and converted into an 80-bin mel-spectrogram so Flow can preserve acoustic context.")], className="input-card"),
                        ],
                        className="input-grid",
                    ),
                ],
                className="content-section frontend-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div([html.Span("01"), html.Span("LANGUAGE → SPEECH PLAN")], className="module-index"),
                            html.H2("LLM: decide what the utterance should sound like."),
                            html.P(
                                "CosyVoice3LM wraps a Qwen2 encoder as an autoregressive speech-token language model. It embeds the requested text, optional prompt text, and reference speech tokens into a shared 896-wide space. Its decoder then samples the next acoustic token repeatedly until an end token is reached.",
                                className="module-lede",
                            ),
                            html.Div(
                                [
                                    html.H3("What it learns for Somali"),
                                    html.P("The LLM carries the highest leverage over pronunciation, lexical timing, phrase boundaries, pauses, and prosodic intent. Punctuation matters here because it becomes evidence for token timing—not a hard-coded silence command."),
                                    html.H3("Why it is fine-tuned"),
                                    html.P("The base model can represent Somali letters, but tokenization is not phonological knowledge. Full-parameter adaptation teaches the mapping from Somali text patterns to the discrete speech-token sequences found in real Somali recordings."),
                                ],
                                className="module-explanation",
                            ),
                        ],
                        className="module-copy",
                    ),
                    html.Aside(
                        [
                            html.Div("IMPLEMENTATION PROFILE", className="eyebrow"),
                            spec("Core", "Qwen2 encoder"),
                            spec("Model width", "896"),
                            spec("Speech vocabulary", "6,561 tokens"),
                            spec("Reserved outputs", "+200 control / stop IDs"),
                            spec("Sampling", "top-p 0.8 · top-k 25"),
                            spec("Token rate", "25 frames / second"),
                            spec("Checkpoint", "llm.pt → llm_somali.pt"),
                        ],
                        className="spec-card llm-spec",
                    ),
                ],
                className="content-section module-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div([html.Span("02"), html.Span("SPEECH PLAN → ACOUSTICS")], className="module-index"),
                            html.H2("Flow: turn symbolic speech into an acoustic surface."),
                            html.P(
                                "CausalMaskedDiffWithDiT embeds the discrete speech tokens, combines them with prompt mel context and the projected speaker embedding, and uses conditional flow matching to generate an 80-channel mel-spectrogram. This representation describes energy across frequency over time—close to sound, but not yet playable audio.",
                                className="module-lede",
                            ),
                            html.Div(
                                [
                                    html.H3("Causal and streamable"),
                                    html.P("The model works in token chunks, with three tokens of look-ahead. A 2:1 token-to-mel ratio expands each 25 Hz speech-token step into mel frames, while cached context avoids rebuilding the whole utterance for every chunk."),
                                    html.H3("What it learns for Somali"),
                                    html.P("Flow adapts timbre, formant structure, local rhythm, energy, and micro-prosody to the Somali corpus and target voices. It cannot reliably invent a pause the LLM never planned, but it determines how naturally that plan is realised."),
                                ],
                                className="module-explanation",
                            ),
                        ],
                        className="module-copy",
                    ),
                    html.Aside(
                        [
                            html.Div("IMPLEMENTATION PROFILE", className="eyebrow"),
                            spec("Architecture", "Causal masked diffusion + DiT"),
                            spec("Mel channels", "80"),
                            spec("DiT", "22 layers · 16 heads"),
                            spec("Hidden width", "1,024"),
                            spec("Speaker input", "192 → 80 projection"),
                            spec("Token : mel", "1 : 2"),
                            spec("Checkpoint", "flow.pt → flow_somali.pt"),
                        ],
                        className="spec-card flow-spec",
                    ),
                ],
                className="content-section module-section reverse-module",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div([html.Span("03"), html.Span("ACOUSTICS → WAVEFORM")], className="module-index"),
                            html.H2("HiFT: render the final waveform without relearning the language."),
                            html.P(
                                "The causal HiFT generator is the vocoder. An F0 predictor estimates pitch from the mel features; a neural source-filter path generates periodic excitation and harmonics; residual upsampling blocks shape the signal; and an inverse short-time Fourier transform reconstructs playable audio at 24 kHz.",
                                className="module-lede",
                            ),
                            html.Div(
                                [
                                    html.H3("Why it stays frozen first"),
                                    html.P("The corpus already matches the base output format: clean, mono, 24 kHz speech. Freezing HiFT preserves a stable renderer while LLM and Flow learn Somali. It also isolates cause: pronunciation errors belong upstream; buzzing or metallic texture may implicate the vocoder."),
                                    html.H3("The unfreeze gate"),
                                    html.P("HiFT is reconsidered only after the LLM produces correct speech tokens and Flow produces stable mel output, yet waveform artifacts persist across speakers and prompts. That would be a separate controlled experiment, not part of the first run."),
                                ],
                                className="module-explanation",
                            ),
                        ],
                        className="module-copy",
                    ),
                    html.Aside(
                        [
                            html.Div("IMPLEMENTATION PROFILE", className="eyebrow"),
                            spec("Generator", "Causal HiFT / HiFi-GAN family"),
                            spec("Conditioning", "80-channel mel"),
                            spec("Pitch", "Causal ConvRNN F0 predictor"),
                            spec("Harmonics", "8"),
                            spec("Upsampling", "8 × 5 × 3"),
                            spec("Output", "24,000 samples / second"),
                            spec("Checkpoint", "hift.pt unchanged"),
                        ],
                        className="spec-card hift-spec",
                    ),
                ],
                className="content-section module-section",
            ),
            html.Section(
                [
                    html.Div("HOW ONE UTTERANCE IS SYNTHESIZED", className="eyebrow"),
                    html.H2("The streaming loop overlaps planning and rendering."),
                    html.Div(
                        [
                            html.Div([html.Span("1"), html.P("Normalise and tokenize the Somali request; analyse the reference voice.")]),
                            html.Div([html.Span("2"), html.P("Start LLM generation in a worker thread and accumulate discrete speech tokens.")]),
                            html.Div([html.Span("3"), html.P("When a token chunk is ready, Flow generates new mel frames with prompt and speaker context.")]),
                            html.Div([html.Span("4"), html.P("HiFT renders the accumulated mel, and the cache emits only waveform samples not already returned.")]),
                            html.Div([html.Span("5"), html.P("Repeat with larger token hops until the LLM ends; finalise the tail without duplicated audio.")]),
                        ],
                        className="synthesis-steps",
                    ),
                ],
                className="content-section synthesis-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div("FIRST SOMALI TRAINING BUNDLE", className="eyebrow"),
                            html.H2("Two adapted checkpoints. One stable renderer."),
                            html.P("Training runs are separate so each contribution can be measured: Somali LLM with base Flow, Somali Flow with base LLM, and both adapted together. The promoted bundle replaces only llm.pt and flow.pt after held-out evaluation."),
                        ],
                        className="bundle-copy",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span("ADAPTED"), html.Strong("llm_somali.pt")]),
                            html.Div([html.Span("ADAPTED"), html.Strong("flow_somali.pt")]),
                            html.Div([html.Span("PRESERVED"), html.Strong("hift.pt")]),
                        ],
                        className="bundle-files",
                    ),
                ],
                className="content-section bundle-section",
            ),
        ],
        className="page cosyvoice-page reading-page",
    )
