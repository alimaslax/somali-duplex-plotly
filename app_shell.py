import dash_mantine_components as dmc
from dash import html

import research_page
import utils.consts as consts


def get_app_shell() -> dmc.AppShell:
    app_shell = dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Title(
                                    consts.WEBSITE_TITLE,
                                    className="main-title",
                                ),
                                html.Span("RESEARCH PAPER", className="header-kicker"),
                            ]
                        ),
                        html.Span("Omar corpus · 2026", className="header-kicker"),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px={"base": "md", "sm": "xl"},
                ),
            ),
            dmc.AppShellMain(research_page.layout(), className="app-main"),
        ],
        header={"height": 58},
        padding=0,
        id="appshell",
    )

    return app_shell
