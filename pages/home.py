import dash
import dash_mantine_components as dmc
from dash import html

import callbacks.home
import components.graphs as graphs
import utils.consts as consts

dash.register_page(__name__, path="/")

def layout(**kwargs) -> html.Div:
    if consts.EXTERNAL_API:
        # NinjasAPI Layout
        return html.Div(
        [
            html.H1(consts.TARGET_COUNTRY + " - Country GDP Data"),
            dmc.Grid(
                children=[
                    dmc.GridCol(
                        graphs.get_graph(index="gdp_growth"),
                        span={"base": 12, "lg": 6},
                    ),
                    dmc.GridCol(
                        graphs.get_graph(index="gdp_nominal"),
                        span={"base": 12, "lg": 6},
                    ),
                    dmc.GridCol(
                        graphs.get_graph(index="gdp_per_capita_nominal"),
                        span={"base": 12, "lg": 6},
                    ),
                    dmc.GridCol(
                        graphs.get_graph(index="gdp_per_capita_ppp"),
                        span={"base": 12, "lg": 6},
                    ),
                ],
            ),
        ],
    )
    else:
        # Gapminder API Layout
        return html.Div(
            [
                html.H1(consts.TARGET_COUNTRY + " - Population Data"),
                dmc.Grid(
                    children=[
                        dmc.GridCol(
                            graphs.get_graph(index="Life Expectancy"),
                            span={"base": 12, "lg": 6},
                        ),
                        dmc.GridCol(
                            graphs.get_graph(index="Population"),
                            span={"base": 12, "lg": 6},
                        ),
                        dmc.GridCol(
                            graphs.get_graph(index="GDP per Capita"),
                            span={"base": 12, "lg": 6},
                        ),
                    ],
                ),
            ],
        )
