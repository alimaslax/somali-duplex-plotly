import plotly.graph_objects as go
import plotly.io as pio
from dash import (
    ALL,
    Input,
    Output,
    Patch,
    State,
    callback,
    no_update,
)

import utils.apis as api
import utils.consts as consts


@callback(
    Output({"type": "graph", "index": ALL}, "figure"),
    Output({"type": "skeleton", "index": ALL}, "visible"),
    Input("_pages_location", "pathname"),
    State("color-scheme-toggle", "checked"),
    State({"type": "graph", "index": ALL}, "id"),
)
def home_load(pathname: str, dark_mode: bool , ids: list[str]) -> tuple[list[go.Figure],list[bool]]:
    figs = []
    skeletons = []
    if pathname == "/":
        country = consts.TARGET_COUNTRY
        # this if statement chooses between using
        # the local gapminder API or the external NinjasAPI
        if consts.EXTERNAL_API:
            df = api.fetch_ninjas_data(country)
        else:
            df = api.fetch_gapminder_data(country)
        for item in ids:
            data = item["index"]
            fig = go.Figure(
                data=go.Bar(
                    x=df.index,
                    y=df[data],
                    showlegend=False,
                )
            )
            fig.update_layout(
                title=dict(
                    text=consts.GRAPH_TITLES[data],
                    x=0.96,
                    font=dict(size=25),
                    subtitle=dict(
                        text=consts.GRAPH_DESCRIPTIONS[data],
                        font=dict(size=18, color="grey"),
                    ),
                ),
                template=pio.templates[consts.DARK_THEME]
                if dark_mode
                else pio.templates[consts.LIGHT_THEME],
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    ticks="outside",
                    tickcolor="lightgray",
                    showline=True,
                    mirror=True,
                    linecolor="lightgray",
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    ticks="outside",
                    tickcolor="lightgray",
                    showline=True,
                    mirror=True,
                    linecolor="lightgray",
                ),
            )
            fig.update_xaxes(
                title=dict(text=f"{df.index.name.title()}", font=dict(size=18))
            )
            fig.update_yaxes(
                title=dict(text=f"{data.replace('_', ' ').title()}", font=dict(size=18))
            )
            figs.append(fig)
            skeletons.append(False)

        return figs, skeletons
    else:
        for item in ids:
            figs.append(no_update)
            skeletons.append(no_update)

        return (figs, skeletons)

@callback(
    Output({"type": "graph", "index": ALL}, "figure", allow_duplicate=True),
    Input("color-scheme-toggle", "checked"),
    State({"type": "graph", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def update_graph_theme(dark_mode: bool, ids: list[str]) -> list[go.Figure]:
    template = (
        pio.templates[consts.DARK_THEME]
        if dark_mode
        else pio.templates[consts.LIGHT_THEME]
    )
    figs = []
    for _ in ids:
        fig = Patch()
        fig.layout.template = template
        figs.append(fig)
    return figs
