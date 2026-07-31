import dash
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

import components.navbar as nav
import callbacks.navbar
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
                                dmc.Burger(
                                    id="burger",
                                    size="sm",
                                    hiddenFrom="sm",
                                    opened=False,
                                ),
                                html.Div("SD", className="brand-mark"),
                                dmc.Title(
                                    consts.WEBSITE_TITLE,
                                    className="main-title",
                                ),
                                html.Span("RESEARCH SYSTEM", className="header-kicker"),
                            ]
                        ),
                        theme_toggle,
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px={"base": "md", "sm": "xl"},
                ),
            ),
            nav.load_navbar(),
            dmc.AppShellMain(dash.page_container, className="app-main"),
            dcc.Location(id="url"),
        ],
        header={"height": 76},
        padding=0,
        navbar={
            "width": 268,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
        id="appshell",
    )

    return app_shell
