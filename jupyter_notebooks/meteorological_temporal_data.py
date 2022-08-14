import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.dates as mdates


def clean_weather_data(path):
    temperature = pd.read_csv(path + 'temperature.csv', sep=';', header = 2, encoding='latin')
    pressure = pd.read_csv(path + 'pressure.csv', sep=';', header = 2, encoding='latin')
    relative_humidity = pd.read_csv(path + 'relative_humidity.csv', sep=';', header = 2, encoding='latin')
    precipitation = pd.read_csv(path + 'precipitation.csv', sep=';', header = 2, encoding='latin')
    solar_radiation = pd.read_csv(path + 'solar_radiation.csv', sep=';', header = 2, encoding='latin')
    wind_speed = pd.read_csv(path + 'wind_speed.csv', sep=';', header = 2, encoding='latin')

    # make list with dataframes
    dframes = []
    dframes += [temperature, pressure, relative_humidity, precipitation, solar_radiation, wind_speed]
    column_names = ['Temperature','Atmospheric pressure','Relative humidity','Precipitation','Solar radiation','Wind speed']

    # remove unnecessary columns, turn date into index
    i = 0
    for df in dframes:
        df.drop(df.columns[[3,4,5,6]], axis=1, inplace=True)
        df.insert(0, 'date', df['Datum'] + ' ' + df['Kl']) # insert a date column with date and hour
        df.drop(['Datum', 'Kl'], axis=1, inplace=True) # drop columns Datum and Kl
        df['date'] = pd.to_datetime(df['date'], format = '%y-%m-%d %H:%M') # change date column to datetime format
        dframes[i].columns.values[1] = column_names[i]
        df.set_index('date', inplace=True) # set date as index column
        i += 1
    
    df_weather = dframes[0]
    for i in range(len(dframes)-1):
        df_weather = df_weather.merge(dframes[i+1], on='date')

    return df_weather

def interpolate_weather(df):
    # weather data is filled with mean linear interpolation OR mean imputation (depending on the look of the time series)
    df['Temperature'] = df['Temperature'].interpolate()
    df['Atmospheric pressure'] = df['Atmospheric pressure'].fillna(df['Atmospheric pressure'].mean())
    df['Relative humidity'] = df['Relative humidity'].interpolate()
    df['Precipitation'] = df['Precipitation'].interpolate()
    df['Solar radiation'] = df['Solar radiation'].interpolate()
    df['Wind speed'] = df['Wind speed'].fillna(df['Wind speed'].mean())
    return df


# sine and cosine of day, week, and year to capture seasonality of pollution data
def add_sine_cosine(df):
    # getting datetime columns and converting to seconds
    timestamp_s = df.index.map(pd.Timestamp.timestamp)
    day = 24*60*60
    week = 7*day
    year = (365.2425)*day
    df['Sine day'] = 0.5*(np.sin(timestamp_s * (2 * np.pi / day))+1)
    df['Cosine day'] = 0.5*(np.cos(timestamp_s * (2 * np.pi / day))+1)
    df['Sine week'] = 0.5*(np.sin(timestamp_s * (2 * np.pi / week))+1)
    df['Cosine week'] = 0.5*(np.cos(timestamp_s * (2 * np.pi / week))+1)
    df['Sine year'] = 0.5*(np.sin(timestamp_s * (2 * np.pi / year))+1)
    df['Cosine year'] = 0.5*(np.cos(timestamp_s * (2 * np.pi / year))+1)
    return df