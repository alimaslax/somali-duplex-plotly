import dash
from dash import html


dash.register_page(
    __name__,
    path="/cosyvoice-3/tokenizer-prosody",
    name="Tokenizer & Prosody",
    title="Somali Duplex — Tokenizer and Prosody",
)


def path_step(label: str, detail: str, tone: str) -> html.Div:
    return html.Div(
        [html.Span(label, className="token-path-label"), html.P(detail)],
        className=f"token-path-step {tone}",
    )


def source_row(path: str, action: str) -> html.Div:
    return html.Div(
        [html.Code(path), html.P(action)],
        className="source-row",
    )


def pause_rule(gap: str, punctuation: str, interpretation: str) -> html.Div:
    return html.Div(
        [html.Strong(gap), html.Code(punctuation), html.P(interpretation)],
        className="pause-rule",
    )


def layout(**kwargs) -> html.Main:
    return html.Main(
        [
            html.Section(
                [
                    html.Div("COSYVOICE 3 / TOKENIZER & PROSODY", className="eyebrow"),
                    html.H1(["The model needs ", html.Em("language evidence"), ", not invented pause tags."]),
                    html.P(
                        "Natural Somali pacing comes from an aligned system: text that preserves real punctuation, prompt audio that preserves speaker context, and training examples where the language model can observe how a speaker actually moves through a sentence. The tokenizer is essential—but it is only one part of that evidence.",
                        className="hero-lede tokenizer-hero-lede",
                    ),
                ],
                className="architecture-hero tokenizer-hero",
            ),
            html.Section(
                [
                    html.Div("TWO TOKENIZATION PATHS", className="eyebrow"),
                    html.H2("Words and sound enter through different doors."),
                    html.P(
                        "CosyVoice 3 receives text tokens for what should be said and separate acoustic tokens for what a reference speaker sounds like. It also receives a speaker embedding and prompt mel features; those are conditioning representations, not text tokens.",
                        className="section-deck",
                    ),
                    html.Div(
                        [
                            html.Article(
                                [
                                    html.Div("TEXT LANE", className="lane-label"),
                                    path_step("Written Somali", "Normal Somali spelling and punctuation enter the CosyVoice frontend.", "text-lane"),
                                    html.Div("↓", className="lane-arrow"),
                                    path_step("Qwen2 BPE", "CosyVoice-BlankEN encodes subword pieces with no unknown-token replacement for ordinary Somali Latin text.", "text-lane"),
                                    html.Div("↓", className="lane-arrow"),
                                    path_step("Text token IDs", "_extract_text_token() passes the encoded sequence to the LLM as the linguistic plan.", "text-lane"),
                                ],
                                className="token-lane",
                            ),
                            html.Article(
                                [
                                    html.Div("AUDIO LANE", className="lane-label"),
                                    path_step("Prompt recording", "A reference clip is loaded at 16 kHz; zero-shot prompt audio is limited to 30 seconds.", "audio-lane"),
                                    html.Div("↓", className="lane-arrow"),
                                    path_step("Whisper log-mel", "The frontend computes a 128-bin Whisper log-mel spectrogram from the prompt audio.", "audio-lane"),
                                    html.Div("↓", className="lane-arrow"),
                                    path_step("speech_tokenizer_v3.onnx", "The ONNX acoustic tokenizer turns prompt features into discrete V3 speech-token IDs used as reference context.", "audio-lane"),
                                ],
                                className="token-lane",
                            ),
                        ],
                        className="token-lanes",
                    ),
                    html.Div(
                        [
                            html.Span("MEET AT THE LLM", className="meet-label"),
                            html.P("The LLM reads the requested Somali text while reference speech tokens and prompt text help establish the requested voice and speaking context. Flow then uses the resulting speech tokens with prompt mel and speaker conditioning to render acoustics."),
                        ],
                        className="token-meet",
                    ),
                ],
                className="content-section token-path-section",
            ),
            html.Section(
                [
                    html.Div(
                        [html.Div("WHAT THE PROJECT IMPORTS", className="eyebrow"), html.H2("One frontend owns the hand-off."), html.P("The local CosyVoice runtime constructs a single CosyVoiceFrontEnd. The YAML selects the Qwen tokenizer and points it at the CampPlus model and the V3 speech-tokenizer ONNX model. The same frontend prepares the tensors for zero-shot, cross-lingual, instruction, and voice-conversion routes."),],
                        className="module-copy",
                    ),
                    html.Aside(
                        [
                            html.Div("RUNTIME TRACE", className="eyebrow"),
                            source_row("cosyvoice/cli/cosyvoice.py", "CosyVoice3 reads cosyvoice3.yaml and creates CosyVoiceFrontEnd."),
                            source_row("cosyvoice3.yaml", "get_tokenizer selects the CosyVoice 3 Qwen tokenizer; the runtime names speech_tokenizer_v3.onnx."),
                            source_row("cosyvoice/cli/frontend.py", "_extract_text_token() calls tokenizer.encode(); _extract_speech_token() runs the V3 ONNX model."),
                            source_row("cosyvoice/tokenizer/tokenizer.py", "get_qwen_tokenizer() loads the bundled Qwen2 BPE assets from CosyVoice-BlankEN."),
                        ],
                        className="spec-card import-trace-card",
                    ),
                ],
                className="content-section module-section import-section",
            ),
            html.Section(
                [
                    html.Div("SOMALI TEXT: WHAT WORKS, WHAT DOES NOT", className="eyebrow"),
                    html.Div(
                        [
                            html.Article(
                                [html.Div("✓", className="truth-mark"), html.H3("Lossless Somali spelling"), html.P("The Qwen2 BPE tokenizer represents ordinary Somali Latin-script text as subword pieces. In local checks, Somali prompts round-tripped exactly with zero unknown tokens. That makes the text valid model input."),],
                                className="truth-card",
                            ),
                            html.Article(
                                [html.Div("×", className="truth-mark"), html.H3("No Somali language control token"), html.P("Do not add <|so|>. The legacy Whisper tokenizer table has a Somali code, but it is not the TTS text tokenizer. For CosyVoice 3, <|so|> is read as literal characters, not a language switch."),],
                                className="truth-card caution-card",
                            ),
                            html.Article(
                                [html.Div("×", className="truth-mark"), html.H3("No exact pause token"), html.P("[PAUSE], <break>, SSML, and ad-hoc markers have no supported pause semantics in the installed path. Literal markup only gives the model unfamiliar text to learn around."),],
                                className="truth-card caution-card",
                            ),
                        ],
                        className="truth-grid",
                    ),
                ],
                className="content-section truths-section",
            ),
            html.Section(
                [
                    html.Div("PROSODY PLAN", className="eyebrow"),
                    html.H2("Use the pauses already spoken in the recordings."),
                    html.P("The proposed pause-alignment workflow derives a new transcript version from ElevenLabs word timestamps. It never changes the audio, source JSON, or original transcript. Instead, it measures real gaps and conservatively inserts ordinary punctuation only after the lexical word sequence has been proven to match.", className="section-deck"),
                    html.Div(
                        [
                            html.Div([html.Span("JSON INPUT", className="pause-flow-label"), html.Code("words[].start / words[].end"), html.P("Use only entries where type is word. Ignore spacing items; retain audio events for review rather than turning them into words.")], className="pause-flow-card"),
                            html.Div("→", className="pause-flow-arrow"),
                            html.Div([html.Span("MEASURE", className="pause-flow-label"), html.Code("next.start − current.end"), html.P("Calculate the gap after each timed word; preserve any unambiguous punctuation already in the canonical text.")], className="pause-flow-card"),
                            html.Div("→", className="pause-flow-arrow"),
                            html.Div([html.Span("DERIVE", className="pause-flow-label"), html.Code("punctuation only"), html.P("Write a new, auditable transcript tree. Any word mismatch is a review flag—not a guess.")], className="pause-flow-card"),
                        ],
                        className="pause-flow",
                    ),
                    html.Div(
                        [
                            pause_rule("< 0.30 s", "—", "Keep the words adjacent. This is normal inter-word timing."),
                            pause_rule("0.30–0.74 s", ",", "A possible short phrase or breath boundary."),
                            pause_rule("0.75–1.39 s", ".", "A clear sentence-like boundary, subject to listening review."),
                            pause_rule("≥ 1.40 s", "… or .", "Use an ellipsis only for audible holding/thinking; otherwise prefer a full stop."),
                        ],
                        className="pause-rules",
                    ),
                    html.Div(
                        [html.Strong("Semantic punctuation remains semantic."), html.P("Timing alone cannot tell a question from a statement. Existing ? and ! survive when they are correct; a long gap must not be mechanically turned into a question.")],
                        className="prosody-note",
                    ),
                ],
                className="content-section prosody-section",
            ),
            html.Section(
                [
                    html.Div(
                        [html.Div("HOW PACING IMPROVES", className="eyebrow"), html.H2("Train the LLM on evidence, then listen for the result."), html.P("During LLM training, punctuation is paired with the real speech-token sequence and real audio timing. Across enough accurate examples, the model can learn that commas, periods, and ellipses correlate with different phrase timing and intonation. This is learned statistical behaviour, not a millisecond-precise command."),],
                        className="module-copy",
                    ),
                    html.Div(
                        [
                            html.Div([html.Span("01"), html.P("Build a new derived transcript version with original text, revised text, threshold version, and every review reason recorded."),]),
                            html.Div([html.Span("02"), html.P("Run a fixed LLM-only comparison: original transcript corpus versus punctuation-aware corpus, same train/dev split and same evaluation prompts."),]),
                            html.Div([html.Span("03"), html.P("Ask Somali listeners to judge phrase breaks, pace, naturalness, names, numbers, questions, and long sentences—not only objective loss."),]),
                            html.Div([html.Span("04"), html.P("Only after LLM pacing improves, retrain and evaluate Flow on the approved derived dataset. Keep the frozen HiFT vocoder as the waveform-quality control."),]),
                        ],
                        className="pacing-steps",
                    ),
                ],
                className="content-section pacing-section",
            ),
        ],
        className="page tokenizer-prosody-page reading-page",
    )
