import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

import utils.consts as consts


def get_app_shell() -> dmc.AppShell:
    theme_toggle = dmc.Switch(
        offLabel=DashIconify(
            icon="radix-icons:sun",
            width=15,
            color=dmc.DEFAULT_THEME["colors"]["yellow"][8],
        ),
        onLabel=DashIconify(
            icon="radix-icons:moon",
            width=15,
            color=dmc.DEFAULT_THEME["colors"]["blue"][6],
        ),
        id="color-scheme-toggle",
        persistence=True,
        color="gray",
        checked=True,
    )

    app_shell = dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                html.Div("SD", className="brand-mark"),
                                dmc.Title(
                                    consts.WEBSITE_TITLE,
                                    className="main-title",
                                ),
                                html.Span("RESEARCH NOTES", className="header-kicker"),
                            ]
                        ),
                        dmc.Group(
                            [
                                html.A("Home", href="/", className="top-nav-link"),
                                html.A("Dataset", href="/dataset", className="top-nav-link"),
                                html.A("CosyVoice 3", href="/cosyvoice-3", className="top-nav-link"),
                                html.A("Tokenizer & prosody", href="/cosyvoice-3/tokenizer-prosody", className="top-nav-link"),
                                theme_toggle,
                            ],
                            gap="lg",
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px={"base": "md", "sm": "xl"},
                ),
            ),
            dmc.AppShellMain(dash.page_container, className="app-main"),
            dcc.Location(id="url"),
        ],
        header={"height": 58},
        padding=0,
        id="appshell",
    )

    return app_shell
