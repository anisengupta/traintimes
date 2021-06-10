# Initial Config
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from apps import config
from apps import app_layout
from apps.app_callbacks import register_app_callbacks, prerequisite_process
from apps import trainline
import pandas as pd
import datetime

# Initiate the app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.UNITED],
)

server = app.server

# Set the title
title = app_layout.make_navbar_title(station=config.STATION)

# Initiate the response
response = prerequisite_process()

# Initiate the service
services = trainline.TrainInformation().get_service(response=response)

# Set the primary message
primary_message_title = app_layout.make_primary_message_title()
# primary_message, links = app_layout.make_prime_message(response=response)

# Make latest train datatable
latest_train_table = app_layout.make_live_table(
    table_id="latest_trains_table_live",
    interval_id="latest_departures_interval_component",
)

# Set the calling points
calling_points_title = app_layout.make_calling_points_title()
calling_points = app_layout.make_calling_points(service=services[0])

calling_points_extra_info_table = app_layout.make_live_table(
    table_id="calling_points_table_live",
    interval_id="calling_points_interval_component",
)

# Set the layout
app_layout_style = {
    "position": "fixed",
    "max-width": "100vw",
    "min-width": "100vw",
    "max-height": "100vh",
    "min-height": "100vh",
    "background-image": "radial-gradient(#697582, #383F49,#383F49)",
}

# Create the row
row = html.Div(
    dbc.Row(
        children=[
            dbc.Col([app_layout.make_digital_clock_card()], width=4),
            dbc.Col([app_layout.make_primary_message_card()]),
            dbc.Col([app_layout.make_api_status_card()]),
        ]
    )
)

# Set the layout
app.layout = html.Div(
    children=[
        title,
        app_layout.make_break(),
        app_layout.make_break(),
        row,
        app_layout.make_break(),
        app_layout.make_break(),
        app_layout.make_latest_departure_title(),
        app_layout.make_break(),
        latest_train_table,
        app_layout.make_break(),
        app_layout.make_break(),
        calling_points_title,
        calling_points_extra_info_table,
    ]
)

# Callbacks
register_app_callbacks(app=app)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
