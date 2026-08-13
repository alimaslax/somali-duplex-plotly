import dash_mantine_components as dmc

import research_page


def get_app_shell() -> dmc.AppShell:
    app_shell = dmc.AppShell(
        [
            dmc.AppShellMain(research_page.layout(), className="app-main"),
        ],
        padding=0,
        id="appshell",
    )

    return app_shell
