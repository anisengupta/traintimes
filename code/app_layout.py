# Initial Config
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import trainline
import pandas as pd
import dash_table
from datetime import datetime
from app_callbacks import prerequisite_process

# Functions
def make_navbar_title(station: str):
    """
    Sets the navigation bar of the page with a title.

    Parameters
    ----------
    station: the name of the station.

    Returns
    -------
    A navbar title.

    """
    # Set today's date
    todays_date = trainline.DatesTimes().custom_strftime("%{S}-%B-%Y", datetime.now())

    navbar = dbc.NavbarSimple(
        children=[dbc.NavItem(dbc.NavLink("Page 1", href="#"))],
        brand=f"Latest train departures from {station} - {todays_date}",
        color="primary",
        className="navbar navbar-expand-lg navbar-dark bg-primary",
    )

    return navbar


def make_break():
    """
    Makes the break in the layout.

    Returns
    -------
    A break in the page.

    """
    return html.Br()


def make_primary_message_title():
    """
    Makes the primary message title.

    Returns
    -------
    The primary message title in the page.

    """
    return html.H2(children="These are the latest messages")


def make_primary_message(response):
    """
    Makes the primary messages to be displayed.

    Parameters
    ----------
    response: the param created via the func create_response.

    Returns
    -------
    The prime message, if there any to be displayed.

    """
    return trainline.TrainInformation().get_primary_message(response=response)


def make_primary_message_card():
    """
    Makes a dbc Card to be displayed with any messages.

    Returns
    -------
    The dbc card to be displayed.

    """
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("These are the latest messages", className="pm_card_title"),
                    html.P(id="live_update_primary_message"),
                ]
            )
        ],
        className="card text-white bg-primary mb-3",
        style={"width": "30rem", "height": "10rem"},
    )

    primary_message_card = html.Div(
        [
            card,
            dcc.Interval(
                id="primary_message_live_update_interval_component",
                interval=1 * 1800000,
                n_intervals=0,
            ),
        ]
    )

    return primary_message_card


def make_digital_clock():
    """
    Makes a digital clock for the Dash app.

    Returns
    -------
    A digital clock in the format of %H:%m:%s.

    """
    digital_clock = html.Div(
        [
            html.Div(id="clock_live_update_text", style={"font-size": "40px"}),
            dcc.Interval(
                id="clock_interval_component", interval=1 * 1000, n_intervals=0
            ),
        ]
    )

    return digital_clock


def make_digital_clock_card():
    """
    Makes the card for the digital clock.

    Returns
    -------
    The dbc card to be displayed.

    """
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Time", className="dc_card_title"),
                    html.P(make_digital_clock()),
                ]
            )
        ],
        className="card text-white bg-info mb-3",
        style={"width": "30rem", "height": "10rem"},
    )

    return card


def make_latest_departure_title():
    """
    Makes the title for the latest departure.

    Returns
    -------
    The latest departure title on the page.

    """
    return html.H2(children="Latest departures")


def make_table(df: pd.DataFrame, id: str) -> dash_table.DataTable:
    """
    Makes a dash datatable from the initial df input.

    Parameters
    ----------
    df: pd.DataFrame, the dataframe input.
    id: str, the id given to the datatable.

    Returns
    -------
    A dash datable on the page.

    """
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        id=id,
        style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
    )

    return table


def make_live_table(table_id: str, interval_id: str):
    """
    Makes a live table to be updated according to the interval param set.

    Parameters
    ----------
    table_id: str, the id given to the live table.
    interval_id: str, the id given to the interval component.

    Returns
    -------

    """
    live_table = html.Div(
        [
            html.Div(id=table_id),
            dcc.Interval(id=interval_id, interval=1 * 1800000, n_intervals=0),
        ]
    )

    return live_table


def make_calling_points_title():
    """
    Makes the title of the calling points.

    Returns
    -------
    The title of the calling points on the page.

    """
    return html.H2(children="Calling at the following stations")


def make_calling_points(service: dict) -> list:
    """
    Makes the calling points based on the service param.

    Parameters
    ----------
    service: dict, created from the response param.

    Returns
    -------
    A list of the stations being called at.

    """
    calling_points = trainline.TrainInformation().calling_points(
        service=service, _type="subsequentCallingPoints"
    )

    return calling_points


def make_api_status_card():
    """
    Makes a dbc Card to be displayed with the status of the LDBWS API.

    Returns
    -------
    The dbc card to be displayed.

    """
    # Initiate the response
    response = prerequisite_process()

    # Evaluate the API status
    status = trainline.TrainInformation().check_api_status(response=response)

    # Assign the className of the card accordingly
    if status:
        class_name = "card text-white bg-success mb-3"
    else:
        class_name = "card text-white bg-danger mb-3"

    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(
                        "Status of the LDBWS API", className="api_status_card_title"
                    ),
                    html.P(id="live_update_api_status"),
                ]
            )
        ],
        className=class_name,
        style={"width": "30rem", "height": "10rem"},
    )

    primary_message_card = html.Div(
        [
            card,
            dcc.Interval(
                id="api_status_live_update_interval_component",
                interval=1 * 1800000,
                n_intervals=0,
            ),
        ]
    )

    return primary_message_card
