# -*- coding: utf-8 -*-

"""
This module provides utility functions for load forecasting project
Author: Andres Felipe Forero Correa
Date: 2023-05-23
"""

import datetime as dt
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import json
import base64
import pandas as pd


def get_datetime_range_by_hour(start_datetime, limit_datetime):
    """Get datetime range hour by hour"""
    datetime_range = [
        start_datetime + dt.timedelta(hours=x)
        for x in range(
            int((limit_datetime - start_datetime).total_seconds() / 3600)
        )
    ]
    return datetime_range


def get_time_df_from_datetime_range(datetime_range, holidays):
    """Create a dataframe with some time parameters using a datetime range"""
    time_df = pd.DataFrame(datetime_range, columns=['datetime'])
    time_df['day_of_week'] = time_df['datetime'].dt.dayofweek
    time_df['holiday'] = time_df['datetime'].map(lambda x: 1 if x in holidays else 0)
    time_df['hour'] = time_df['datetime'].dt.hour
    return time_df


def fetch_json(url):
    """Fetch JSON data from url request"""
    try:
        with urlopen(url) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except HTTPError as error:
        print(f"HTTPError: {error.code}")
        return False
    except URLError as error:
        print(f"URLError: {error}")
        return False


def get_weather_df_from_open_meteo_json(json_data):
    """Create a weather dataframe extracting json data (from Open Meteo API)"""
    weather_df = pd.DataFrame()
    for param in json_data['hourly_units'].keys():
        param_unit = f"{param} ({json_data['hourly_units'][param]})"
        weather_df[param_unit] = json_data['hourly'][param]
    param_time = f"time ({json_data['hourly_units']['time']})"
    weather_df['datetime'] = pd.to_datetime(weather_df[param_time])
    weather_df = weather_df.drop(columns=[param_time])
    return weather_df


def create_download_link(val, filename):
    """Create a download link using html code"""
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" \
        download="{filename}.csv">Download CSV</a>'
