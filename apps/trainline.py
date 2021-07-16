# Initial Config
from typing import Tuple, Any
from zeep import Client
from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime
import time

# Functions for getting all data via the LDBWS API (https://lite.realtime.nationalrail.co.uk/OpenLDBWS/)
class DatesTimes:
    """
    Class gets today's date and times.

    """

    def __init__(self):
        pass

    @staticmethod
    def suffix(d: int):
        """
        Returns the suffix based on the day. Eg 9th of October, or
        3rd of December.

        Parameters
        ----------
        d: int, the day param.

        Returns
        -------
        The correct suffix based on the day param input.

        """
        return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")

    @staticmethod
    def custom_strftime(format: str, t: datetime):
        """
        Adds a custom suffix after the day.

        Parameters
        ----------
        format: str, the format of the time.
        t: the datetime object.

        Returns
        -------

        """
        return t.strftime(format).replace(
            "{S}", str(t.day) + DatesTimes.suffix(t.day)
        )


class CRSNames:
    """
    Class retrieves the CRS name for a station based on the website:
    https://www.nationalrail.co.uk/stations_destinations/48541.aspx

    """

    def __init__(self):
        pass

    @staticmethod
    def make_station_dataframe(url: str) -> pd.DataFrame:
        """
        Initiates a request and returns a dataframe with station names and their crs
        codes.

        Parameters
        ----------
        url: str, the url from which the data is to be retrieved.

        Returns
        -------
        A pandas dataframe.

        """
        # Initiate the request
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        r = requests.get(url, headers=header)

        # Construct the dataframe
        df = pd.read_html(r.text)[5]
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        return df

    @staticmethod
    def get_station_list(df: pd.DataFrame) -> list:
        """
        Returns a list of stations from the pandas dataframe input, made from the
        make_station_dataframe func.

        Parameters
        ----------
        df: a pandas dataframe input, made from the func make_station_dataframe.

        Returns
        -------
        A list of station names.

        """
        return df["Station Name"].unique().tolist()

    @staticmethod
    def make_crs_dict(url: str) -> dict:
        """
        Makes a dictionary of station names in the UK and their respective CRS apps.

        Parameters
        ----------
        url: str, the url from which the data is to be retrieved.

        Returns
        -------
        A dictionary of the station names and crs codes.

        """
        # Initiate the request and construct dataframe
        df = CRSNames.make_station_dataframe(url=url)

        # Make lists
        station_names = CRSNames.get_station_list(df=df)
        crs_codes = df["CRS Code"]

        # Construct the dictionary
        return dict(zip(station_names, crs_codes))

    @staticmethod
    def lookup_crs_name(station: str, crs_dict: dict) -> str:
        """
        Looks up the crs name based on the station param.

        Parameters
        ----------
        station: str, the name of the station to look up.
        crs_dict: dict, the dictionary of station names and crs codes.

        Returns
        -------
        A string with the crs apps of the station name specified.

        """
        try:
            return crs_dict.get(station)
        except:
            return "No CRS apps found"


class TrainInformation:
    """
    Class initiates the SOAP client, creates the appropriate headers and gets all the relevant train
    information.

    """

    def __init__(self):
        pass

    @staticmethod
    def make_data_dict(station: str, url: str):
        """
        Makes a dictionary of the data to be passed off to the
        SOAP API.

        Parameters
        ----------
        station: str, the name of the station to look up.
        url: str, the url to get CRS codes for stations.

        Returns
        -------
        A dictionary to be passed to the API.

        """
        crs_dict = CRSNames.make_crs_dict(url=url)
        crs_code = CRSNames.lookup_crs_name(station=station, crs_dict=crs_dict)
        data_dict = {"numRows": "10", "crs": crs_code, "filterType": "from"}

        return data_dict

    @staticmethod
    def initiate_client(url: str):
        """
        Initiates the SOAP client using the url param.

        Parameters
        ----------
        url: str, the url of the SOAP API to be initiated.

        Returns
        -------
        An initiated client, ready to parse SOAP API requests.

        """
        return Client(url)

    @staticmethod
    def create_soap_headers(token: str) -> dict:
        """
        Creates the headers needed to initialise the SOAP API request.

        Parameters
        ----------
        token: str, the token needed for the request.

        Returns
        -------

        """
        return {"AccessToken": token}

    @staticmethod
    def create_response(data: dict, soap_headers: dict, client) -> dict:
        """
        Creates the response from the API using the soap_headers param and the data param.

        Parameters
        ----------
        data: dict, a dict of data to be passed off.
        soap_headers: dict, the soap headers to be passed off.
        client: the SOAP client, initiated using the func initiate_client.

        Returns
        -------
        A response with the data requested,.

        """
        return client.service.GetArrDepBoardWithDetails(
            **data, _soapheaders=soap_headers
        )

    @staticmethod
    def check_api_status(response) -> bool:
        """
        Checks the status of the API call by evaluating the response dict created
        from the func create_response.

        Parameters
        ----------
        response: the param created via the func create_response.

        Returns
        -------
        A bool, either True if the API connection is successful, False if there
        is a problem.

        """
        return bool(response)

    @staticmethod
    def get_primary_message(response: dict) -> Tuple[Any, list]:
        """
        Returns the primary messages from the API call.

        Parameters
        ----------
        response: the param created via the func create_response.

        Returns
        -------
        A string an

        """
        try:
            # Parse the response via Beautiful Soup
            soup = BeautifulSoup(
                response["nrccMessages"]["message"][0]["_value_1"], "html.parser"
            )

            # Make a message string
            message_str = soup.get_text().replace("\n", "")

            # Make a list of any links
            links = []
            for link in soup.find_all("a"):
                links.append(link.get("href"))
        except:
            message_str = "No message"
            links = []

        return message_str, links

    @staticmethod
    def get_service(response: dict) -> list:
        """
        Returns a list of services using the response param created.

        Parameters
        ----------
        response: the param created via the func create_response.

        Returns
        -------

        """
        return response["trainServices"]["service"]

    @staticmethod
    def get_closest_service(response: dict) -> dict:
        """
        Returns a service using the response param created.

        Parameters
        ----------
        response: the param created via the func create_response.

        Returns
        -------
        A service ready to be parsed.

        """
        return response["trainServices"]["service"][0]

    @staticmethod
    def get_starting_time(service: dict) -> str:
        """
        Returns the starting time of the train.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        A str of the starting time.

        """
        return service["sta"]

    @staticmethod
    def get_status(service: dict) -> str:
        """
        Returns the status of the train.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        A str of the status.

        """
        return service["eta"]

    @staticmethod
    def get_platform_number(service: dict) -> str:
        """
        Gets the platform number of the train.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        The platform number of the train.

        """
        return service["platform"]

    @staticmethod
    def get_train_operator(service: dict) -> str:
        """
        Gets the train operator the departing train.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        The operator of the departing train.

        """
        return service["operator"]

    @staticmethod
    def get_origin_name(service: dict) -> str:
        """
        Returns the name of the origin station.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        The name of the origin station.

        """
        return service["origin"]["location"][0]["locationName"]

    @staticmethod
    def get_destination(service: dict) -> str:
        """
        Returns the name of the destination station.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        The name of the destination station.

        """
        return service["destination"]["location"][0]["locationName"]

    @staticmethod
    def check_train_cancellation(service: dict):
        cancellation_status = service['isCancelled']
        cancel_reason = service['cancelReason']
        delay_reason = service['delayReason']

        return cancellation_status, cancel_reason, delay_reason

    @staticmethod
    def calling_points(service: dict, _type: str) -> list:
        """
        Gets the calling points based on the _type param.

        Parameters
        ----------
        service: dict, created from the response param.
        _type: str, can be 'previousCallingPoints' or 'subsequentCallingPoints'.

        Returns
        -------
        A list of calling point stations.

        """
        # Check if there is a cancellation/delay
        initiate_calling_points = service[_type]

        if initiate_calling_points is None:
            cancellation_status, cancel_reason, delay_reason = TrainInformation.check_train_cancellation(
                service=service
            )

            return cancel_reason
        else:
            calling_points = initiate_calling_points["callingPointList"][0]["callingPoint"]

            calling_point_stations = []

            for calling_point in calling_points:
                location_name = calling_point["locationName"]
                calling_point_stations.append(location_name)

            return calling_point_stations

    @staticmethod
    def calling_times(service: dict, _type: str):
        """
        Gets the times of the calling points based on the _type param.

        Parameters
        ----------
        service: dict, created from the response param.
        _type: str, can be 'previousCallingPoints' or 'subsequentCallingPoints'.

        Returns
        -------
        A list of the calling point times.

        """
        # Check if there is a cancellation/delay
        initiate_calling_points = service[_type]

        if initiate_calling_points is None:
            cancellation_status, cancel_reason, delay_reason = TrainInformation.check_train_cancellation(
                service=service
            )

            return cancel_reason
        else:
            calling_points = initiate_calling_points["callingPointList"][0]["callingPoint"]

            calling_point_times = []

            for calling_point in calling_points:
                time = calling_point["st"]
                calling_point_times.append(time)

            return calling_point_times

    @staticmethod
    def calling_status(service: dict, _type: str) -> list:
        """
        Gets the status of the calling points based ont eh _type param.
        Parameters
        ----------
        service: dict, created from the response param.
        _type: str, can be 'previousCallingPoints' or 'subsequentCallingPoints'.

        Returns
        -------
        A list of the calling point status.

        """
        # Check if there is a cancellation/delay
        initiate_calling_points = service[_type]

        if initiate_calling_points is None:
            cancellation_status, cancel_reason, delay_reason = TrainInformation.check_train_cancellation(
                service=service
            )

            return cancel_reason
        else:
            calling_points = initiate_calling_points["callingPointList"][0]["callingPoint"]

            calling_point_status = []

            for calling_point in calling_points:
                status = calling_point["et"]
                calling_point_status.append(status)

            return calling_point_status

    @staticmethod
    def make_traintimes_dict(service: dict, station: str) -> dict:
        """
        Makes a dictionary of the train times.

        Parameters
        ----------
        service: dict, created from the response param.
        station: the name of the station.

        Returns
        -------
        A dictionary of the train times and all the relevant information.

        """
        def handle_eta_key():
            """
            Handles the ETA key creation. If there is a cancellation, then this
            is handled so that the cancellation message is returned.

            Returns
            -------
            A string, with either the ETA or the reason for cancellation/delay.

            """
            eta = TrainInformation.calling_times(service, "subsequentCallingPoints")
            check_list = isinstance(eta, list)

            if check_list:
                return eta[-1]
            else:
                return eta

        df_dict = {
            "Station": station,
            "Origin": TrainInformation.get_origin_name(service=service),
            "Destination": TrainInformation.get_destination(service=service),
            "Starting_Time": TrainInformation.get_starting_time(service=service),
            "ETA": handle_eta_key(),
            "Status": TrainInformation.get_status(service=service),
            "Platform": TrainInformation.get_platform_number(service=service),
            "Operator": TrainInformation.get_train_operator(service=service),
        }

        return df_dict

    @staticmethod
    def make_calling_times_df(service: dict) -> pd.DataFrame:
        """
        Makes a dataframe of the calling station, times and statuses.

        Parameters
        ----------
        service: dict, created from the response param.

        Returns
        -------
        A dictionary of the subsequent calling points and the relevant information.

        """
        # Initiate the dataframe
        df_calling_points = pd.DataFrame(columns=["Calling_At", "Time", "Status"])

        # Get all the information
        df_calling_points["Calling_At"] = TrainInformation.calling_points(
            service, "subsequentCallingPoints"
        )
        df_calling_points["Time"] = TrainInformation.calling_times(
            service, "subsequentCallingPoints"
        )
        df_calling_points["Status"] = TrainInformation.calling_status(
            service, "subsequentCallingPoints"
        )

        return df_calling_points

    @staticmethod
    def get_latest_departures_df(services: list,
                                 station: str
                                 ) -> pd.DataFrame:
        """
        Gets the latest number of departures based on the API call.

        Parameters
        ----------
        services: dict, the dictionary constructed from the API call.
        station: str, the name of the station.

        Returns
        -------
        A pandas dataframe with the latest trains and their destinations.

        """
        df_list = []

        for service in services:
            train_dict = TrainInformation.make_traintimes_dict(
                service=service, station=station
            )
            df = pd.DataFrame.from_dict(train_dict, orient="index").T
            df_list.append(df)

        return pd.concat(df_list, axis=0)

