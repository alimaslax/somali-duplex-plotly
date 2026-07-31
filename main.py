import dash_mantine_components as dmc
from dash import Dash

import app_shell
import callbacks.clientside
import utils.consts as consts
from utils.settings import APP_DEBUG

dashboard = Dash(
    __name__,
    title=consts.WEBSITE_TITLE,
    external_stylesheets=dmc.styles.ALL,
    use_pages=True,
)

dmc.add_figure_templates()

dashboard.layout = dmc.MantineProvider(children=[app_shell.get_app_shell()])


if __name__ == "__main__":
    dashboard.run(debug=APP_DEBUG)
