# Initial Config
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from config import URL, TOKEN, STATION, CRS_URL
import app_layout
import trainline
import pandas as pd
import datetime

# Prerequisite functions
def prerequisite_process():
    """
    Instantiates the pre-requisite steps to obtaining data.

    Returns
    -------
    A requests.response object.

    """
    # Initiate the client
    client = trainline.TrainInformation().initiate_client(url=URL)

    # Create the SOAP Headers
    soap_headers = trainline.TrainInformation().create_soap_headers(token=TOKEN)

    # Make the data
    DATA = trainline.TrainInformation().make_data_dict(station=STATION, url=CRS_URL)

    # Initiate the response
    response = trainline.TrainInformation().create_response(
        data=DATA, soap_headers=soap_headers, client=client
    )

    return response


# Callback functions
def register_app_callbacks(app):
    """
    Registers the callbacks for app_layout.py

    Parameters
    ----------
    app: the Dash App initialized.

    Returns
    -------
    The callbacks functions for the Dash App.

    """

    # Digital Clock callback
    @app.callback(
        Output("clock_live_update_text", "children"),
        [Input("clock_interval_component", "n_intervals")],
    )
    def update_date(n):
        """
        Updates the time on the Dash page every second.

        Parameters
        ----------
        n: the intervals from the callback.

        Returns
        -------
        A time that is updated every second.

        """
        now = datetime.datetime.now()
        now_str = now.strftime("%H:%M:%S")

        return [html.P(now_str)]

    @app.callback(
        Output("latest_trains_table_live", "children"),
        Input("latest_departures_interval_component", "n_intervals"),
    )
    def update_latest_departures_table(n):
        """
        Updates the latest departures table on an interval.

        Parameters
        ----------
        n: the intervals from the callback.

        Returns
        -------
        The latest departure table updated on an interval.

        """
        # Initiate the response
        response = prerequisite_process()

        # Initiate the service
        services = trainline.TrainInformation().get_service(response=response)

        # Get the latest train dataframe
        latest_trains_df = trainline.TrainInformation().get_latest_departures_df(
            services=services
        )

        # Make latest train datatable
        latest_train_table = app_layout.make_table(
            df=latest_trains_df,
            id="latest_trains_table",
        )

        return html.Div([latest_train_table])

    @app.callback(
        Output("calling_points_table_live", "children"),
        Input("calling_points_interval_component", "n_intervals"),
    )
    def update_calling_points_departures_table(n):
        """
        Updates the calling points departure table on an interval.

        Parameters
        ----------
        n: the intervals from the callback.

        Returns
        -------
        The calling points departure table updated on an interval.

        """
        # Initiate the response
        response = prerequisite_process()

        # Initiate the service
        service = trainline.TrainInformation().get_closest_service(response=response)

        # Set the calling point dataframe
        calling_points_extra_info_df = (
            trainline.TrainInformation().make_calling_times_df(service=service)
        )

        # Make latest train datatable
        calling_points_extra_info_table = app_layout.make_table(
            df=calling_points_extra_info_df,
            id="calling_points_table",
        )

        return html.Div([calling_points_extra_info_table])

    @app.callback(
        Output("live_update_primary_message", "children"),
        Input("primary_message_live_update_interval_component", "n_intervals"),
    )
    def update_primary_message(n):
        """
        Updates the primary messages card on an interval.

        Parameters
        ----------
        n: the intervals from the callback.

        Returns
        -------
        The primary messages card updated on the hour.

        """
        # Initiate the response
        response = prerequisite_process()

        return html.Div(
            trainline.TrainInformation().get_primary_message(response=response)
        )

    @app.callback(
        Output("live_update_api_status", "children"),
        Input("api_status_live_update_interval_component", "n_intervals"),
    )
    def update_api_status(n):
        """
        Updated the API status on an interval.

        Parameters
        ----------
        n: the intervals from the callback.

        Returns
        -------
        The API status card updated on an interval.

        """
        # Initiate the response
        response = prerequisite_process()

        # Evaluate the API status
        status = trainline.TrainInformation().check_api_status(response=response)

        if status:
            card_text = "All services running correctly"
        else:
            card_text = "Warning, there is a problem, please investigate"

        return html.Div(card_text)
