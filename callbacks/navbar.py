from dash import Input, Output, State, callback
import dash_mantine_components as dmc


@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened: bool, navbar: dmc.AppShellNavbar) -> dmc.AppShellNavbar:
    navbar["collapsed"] = {"mobile": not opened}
    return navbar
