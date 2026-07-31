import pandas as pd
import plotly.express as px
import requests

from utils.settings import NINJAS_API_KEY


def fetch_gapminder_data(country: str) -> pd.DataFrame:
    df = px.data.gapminder(pretty_names=True, return_type="pandas")
    df.set_index("Year", inplace=True)
    df = df[df["Country"] == country]
    df["Population"] = df["Population"] / 1e6
    return df


def fetch_ninjas_data(country: str) -> pd.DataFrame:
    # API parameters and URL
    api_url = "https://api.api-ninjas.com/v1/gdp"
    api_key = NINJAS_API_KEY

    # Set headers
    headers = {"X-Api-Key": api_key}

    # Construct the query parameters
    querystring = {
        "country": country,
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=querystring)

    # Check if the request was successful
    # NOTE: bear in mind that the failure for data to return from the 
    # API request should be handled more comprehensively than this!
    if response.status_code == requests.codes.ok:
        df = pd.DataFrame(response.json())
        df.set_index("year", inplace=True)
        return df
    else:
        return None
