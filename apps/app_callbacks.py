# Initial Config
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from apps.config import URL, TOKEN, STATION, CRS_URL
import apps.app_layout as app_layout
import apps.trainline as trainline
import pandas as pd
import datetime

# Prerequisite functions
def prerequisite_process(station: str):
    """
    Instantiates the pre-requisite steps to obtaining data.

    Parameters
    ----------
    station: str, the name of the station.

    Returns
    -------
    A requests.response object.

    """
    # Initiate the client
    client = trainline.TrainInformation.initiate_client(url=URL)

    # Create the SOAP Headers
    soap_headers = trainline.TrainInformation.create_soap_headers(token=TOKEN)

    # Make the data
    DATA = trainline.TrainInformation.make_data_dict(station=station, url=CRS_URL)

    # Initiate the response
    response = trainline.TrainInformation.create_response(
        data=DATA, soap_headers=soap_headers, client=client
    )

    return response


def handle_submit_button_status(submit, station_value: str):
    """
    Handle the returning and updating of data only when the Submit is clicked
    and the station_value input in the Change Station modal has been populated.

    Parameters
    ----------
    submit: the submit button being clicked.
    station_value: the station input in the Change Station modal.

    Returns
    -------
    The station and the relevant response

    """
    # Initiate the response
    if submit is None:
        station = STATION
        response = prerequisite_process(station=station)
    elif submit is None and station_value is None:
        station = STATION
        response = prerequisite_process(station=station)
    else:
        station = station_value
        response = prerequisite_process(station=station)

    return station, response


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
        now = datetime.datetime.now() + datetime.timedelta(hours=1)
        now_str = now.strftime("%H:%M:%S")

        return [html.P(now_str)]

    @app.callback(
        Output("latest_trains_table_live", "children"),
        [Input("latest_departures_interval_component", "n_intervals"),
         Input('change_station_modal_input', 'value'),
         Input('change_station_modal_submit', 'n_clicks')]
    )
    def update_latest_departures_table(n, station_value: str, submit):
        """
        Updates the latest departures table on an interval.

        Parameters
        ----------
        n: the intervals from the callback.
        station_value: str, the name of the station, if needs changing.

        Returns
        -------
        The latest departure table updated on an interval.

        """
        # Initiate the response
        station, response = handle_submit_button_status(submit=submit,
                                                        station_value=station_value)

        # Initiate the service
        services = trainline.TrainInformation.get_service(response=response)

        latest_trains_df = trainline.TrainInformation.get_latest_departures_df(
            services=services,
            station=station
        )

        # Make latest train datatable
        latest_train_table = app_layout.make_table(
            df=latest_trains_df,
            id="latest_trains_table",
        )

        return html.Div([latest_train_table])

    @app.callback(
        Output("calling_points_table_live", "children"),
        [Input("calling_points_interval_component", "n_intervals"),
         Input('change_station_modal_input', 'value'),
         Input('change_station_modal_submit', 'n_clicks')]
    )
    def update_calling_points_departures_table(n, station_value: str, submit):
        """
        Updates the calling points departure table on an interval.

        Parameters
        ----------
        n: the intervals from the callback.
        station_value: str, the name of the station, if needs changing.

        Returns
        -------
        The calling points departure table updated on an interval.

        """
        # Initiate the response
        # Initiate the response
        station, response = handle_submit_button_status(submit=submit,
                                                        station_value=station_value)

        # Initiate the service
        service = trainline.TrainInformation.get_closest_service(response=response)

        # Set the calling point dataframe
        calling_points_extra_info_df = (
            trainline.TrainInformation.make_calling_times_df(service=service)
        )

        # Make latest train datatable
        calling_points_extra_info_table = app_layout.make_table(
            df=calling_points_extra_info_df,
            id="calling_points_table",
        )

        return html.Div([calling_points_extra_info_table])

    @app.callback(
        Output("live_update_primary_message", "children"),
        [Input("primary_message_live_update_interval_component", "n_intervals"),
         Input('change_station_modal_input', 'value'),
         Input('change_station_modal_submit', 'n_clicks')]
    )
    def update_primary_message(n, station_value: str, submit):
        """
        Updates the primary messages card on an interval.

        Parameters
        ----------
        n: the intervals from the callback.
        station_value: str, the name of the station, if needs changing.

        Returns
        -------
        The primary messages card updated on the hour.

        """
        # Initiate the response
        # Initiate the response
        station, response = handle_submit_button_status(submit=submit,
                                                        station_value=station_value)

        return html.Div(
            trainline.TrainInformation.get_primary_message(response=response)
        )

    @app.callback(
        Output("live_update_api_status", "children"),
        [Input("api_status_live_update_interval_component", "n_intervals"),
         Input('change_station_modal_input', 'value'),
         Input('change_station_modal_submit', 'n_clicks')]
    )
    def update_api_status(n, station_value: str, submit):
        """
        Updated the API status on an interval.

        Parameters
        ----------
        n: the intervals from the callback.
        station_value: str, the name of the station, if needs changing.

        Returns
        -------
        The API status card updated on an interval.

        """
        # Initiate the response
        # Initiate the response
        station, response = handle_submit_button_status(submit=submit,
                                                        station_value=station_value)

        # Evaluate the API status
        status = trainline.TrainInformation.check_api_status(response=response)

        if status:
            card_text = "All services running correctly"
        else:
            card_text = "Warning, there is a problem, please investigate"

        return html.Div(card_text)

    @app.callback(
        Output('change_station_modal', 'is_open'),
        [Input('change_station_modal_open', 'n_clicks'),
         Input('change_station_modal_close', 'n_clicks')
         ],
        State('change_station_modal', 'is_open')
    )
    def toggle_change_station_modal(n1, n2, is_open):
        """
        Opens and closes the Change Station modal.

        Parameters
        ----------
        n1: the open modal button click.
        n2: the close modal button click.
        is_open: the state of the modal

        Returns
        -------
        A dbc Modal that opens and closes.

        """
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output('title', 'brand'),
        [Input('change_station_modal_input', 'value'),
         Input('change_station_modal_submit', 'n_clicks')
         ],
        State('change_station_modal', 'is_open')
    )
    def update_title(value, submit, is_open):
        """
        Updates the title according to the change station modal.

        Parameters
        ----------
        value: the station name value inputted from the modal.
        submit: the submit button click
        is_open: if the change status modal is open

        Returns
        -------
        The title of the page updated accordingly.

        """
        # Set today's date
        todays_date = trainline.DatesTimes.custom_strftime("{S}-%B-%Y", datetime.datetime.now())

        if submit is None:
            station = STATION
            brand = f"Latest train departures from {station} - {todays_date}"
            return brand, is_open
        else:
            brand = f"Latest train departures from {value} - {todays_date}"
            return brand, not is_open
