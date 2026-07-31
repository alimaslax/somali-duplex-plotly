import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def load_navbar() -> dmc.AppShellNavbar:
    return dmc.AppShellNavbar(
        id="navbar",
        children=[
            html.Div("DOCUMENTATION", className="nav-eyebrow"),
            html.Div(
                className="nav-links",
                children=[
                    dmc.NavLink(
                        label="Home",
                        description="Mission, data, and pipeline",
                        href="/",
                        active="exact",
                        leftSection=DashIconify(
                            icon="ph:waveform-bold",
                            width=21,
                        ),
                        className="project-nav-link",
                    ),
                    html.Div(
                        [
                            dmc.NavLink(
                                label="CosyVoice 3",
                                description="Model architecture and synthesis",
                                href="/cosyvoice-3",
                                active="exact",
                                leftSection=DashIconify(icon="ph:circles-three-plus-bold", width=21),
                                className="project-nav-link cosyvoice-parent-link",
                            ),
                            html.Div(
                                [
                                    html.Div("IN THIS SECTION", className="submenu-label"),
                                    dmc.NavLink(
                                        label="Tokenizer & prosody",
                                        description="Text, audio tokens, and natural pacing",
                                        href="/cosyvoice-3/tokenizer-prosody",
                                        active="exact",
                                        leftSection=DashIconify(icon="ph:waveform-bold", width=16),
                                        className="project-nav-link project-subnav-link",
                                    ),
                                ],
                                className="cosyvoice-submenu",
                            ),
                        ],
                        className="nav-group",
                    ),
                ],
            ),
            html.Div(
                [
                    html.Div("CURRENT DIRECTION", className="nav-eyebrow"),
                    html.P(
                        "Adapt the language and acoustic stack for Somali; keep waveform rendering stable.",
                        className="nav-note-copy",
                    ),
                    html.Div(
                        [html.Span(className="status-dot"), html.Span("LLM + Flow adaptation")],
                        className="nav-status",
                    ),
                ],
                className="nav-note",
            ),
        ],
        p="lg",
    )
