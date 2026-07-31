import dash_mantine_components as dmc
from dash import dcc


def get_graph(index: str) -> dmc.Skeleton:
    return dmc.Skeleton(
                id={"type": "skeleton", "index": index},
                visible=True,
                children=dmc.AspectRatio(
                    dcc.Graph(id={"type": "graph", "index": index}, responsive=True),
                    ratio=1.618034,
                ),
                mb=10,
            )