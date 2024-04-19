# -*- coding: utf-8 -*-

"""
Energy Load Forecasting: web app that predicts kW values
according to weather and time variables.
Author: Andres Felipe Forero Correa
Date: 2023-05-05
"""

import datetime as dt
import pickle
import copy
import holidays
import plotly.express as px
import streamlit as st
from functions import get_datetime_range_by_hour,\
    get_time_df_from_datetime_range,\
    fetch_json, get_weather_df_from_open_meteo_json,\
    create_download_link
import warnings
warnings.filterwarnings("ignore", message=".*XGBoost.*")

if __name__ == "__main__":
    # Constants
    FORECAST_DAYS = 7
    # Page title, title and caption of the web app
    st.set_page_config(page_title="Energy Load Forecasting", page_icon="🤖")
    st.title("Energy Load Forecasting")
    st.caption("Machine Learning model that predicts energy loads of Villavicencio city (Colombia).")
    # Define by default 7 days of prediction
    min_date = dt.date.today()
    max_date = min_date + dt.timedelta(days=FORECAST_DAYS-1)
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
    # Check the input dates are correct
    if start_date > end_date:
        st.error("ERROR: 'End date' must be greater or equal to 'Start date'.", icon="🚨")
        st.stop()
    # ####### CORE PROCESSING ####### #
    if st.button('Predict'):
        # Define start, end and limit datime for datetime range
        start_datetime = dt.datetime.combine(start_date, dt.datetime.min.time())
        end_datetime = dt.datetime.combine(end_date, dt.datetime.min.time())
        limit_datetime = end_datetime + dt.timedelta(days=1)
        # Define datetime range
        datetime_range = get_datetime_range_by_hour(start_datetime, limit_datetime)
        # Define a dataframe with all time parameters
        co_holidays = holidays.CO()
        time_df = get_time_df_from_datetime_range(datetime_range, co_holidays)
        time_df = time_df.set_index('datetime')
        # Retrieve weather data using Open Meteo API
        #config = dotenv_values(".env")
        open_meteo_api_url = 'https://api.open-meteo.com/v1/forecast?latitude=4.14&longitude=-73.63&timezone=America/Bogota&hourly=temperature_2m,relativehumidity_2m,precipitation,windgusts_10m'
        json_data = fetch_json(open_meteo_api_url)
        # Define weather dataframe from JSON data
        weather_df = get_weather_df_from_open_meteo_json(json_data)
        weather_df = weather_df.set_index('datetime')
        # Join time and weather dataframes
        input_df = time_df.join(weather_df)
        # Load Machine Learning model from *.sav file
        with open('ml_villavicencio_2016_jan_aug.sav', 'rb') as f:
            reg_model = pickle.load(f)
        # Define X and X + y dataframe
        X_df = input_df.loc[start_datetime:limit_datetime]
        Xy_df = copy.deepcopy(X_df)
        Xy_df = Xy_df.reset_index()
        Xy_df['date'] = Xy_df['datetime'].dt.strftime('%Y-%m-%d')
        Xy_df = Xy_df.set_index('datetime')
        # Make a prediction into X + y dataframe
        Xy_df['kW'] = reg_model.predict(X_df)
        # Fix Xy_df
        Xy_df = Xy_df.reset_index()
        # Create A_df
        A_df = Xy_df.copy(deep=True)
        A_df = A_df[['datetime', 'holiday', 'temperature_2m (°C)', 'relativehumidity_2m (%)', 'kW']]
        week_day_df = A_df['datetime'].dt.dayofweek
        # A_df.insert(1, 'dia_semana', week_day_df.map(dias_semana_dict))
        # Map festivo to 'Si' / 'No'
        A_df['holiday'] = A_df['holiday'].map({0: 'No', 1: 'Yes'})
        # Add MW to A_df
        A_df['MW'] = A_df['kW'] * 0.001
        # Round kW and MW
        A_df['kW'] = A_df['kW'].astype(float).round(2)
        A_df['MW'] = A_df['MW'].astype(float).round(2)
        # A_df in front end
        A_df = A_df.set_index('datetime')
        st.header('Prediction dataframe')
        st.dataframe(A_df)
        # A_df as Download CSV link
        A_df = A_df.reset_index()
        min_date = A_df['datetime'].min().strftime('%Y-%m-%d')
        max_date = A_df['datetime'].max().strftime('%Y-%m-%d')
        csv_output = A_df.to_csv(index=False).encode('utf-8')
        download_url = create_download_link(csv_output, f'load_forecast_{min_date}_to_{max_date}')
        st.markdown(download_url, unsafe_allow_html=True)
        # Show load curves per day
        Xy_df = Xy_df.set_index('datetime')
        st.header('Prediction curves per day')
        fig = px.line(Xy_df, x="hour", y="kW", color='date', markers=True)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        # Select date to show load curves per day
        st.header("Hourly prediction values")
        Xy_df = Xy_df.reset_index()
        dates_list = list(Xy_df['date'].unique())
        for elem in dates_list:
            mini_df = Xy_df[Xy_df['date'] == elem]
            date = mini_df['datetime'].astype(object).unique()[0].strftime("%Y-%m-%d")
            week_day = mini_df['datetime'].astype(object).unique()[0].strftime("%A")
            fig = px.bar(mini_df, x='hour', y='kW', color='kW')
            st.subheader(f"{date}, {week_day}")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
