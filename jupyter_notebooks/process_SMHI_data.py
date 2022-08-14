import pandas as pd
import numpy as np

import glob
from functools import reduce

"""Script for cleaning up dataframes downloaded in SMHI format"""

def dataframes(path):
    files = glob.glob(path + '*.csv') # name and all files downloaded from SHMI open data
    dframes = []
    for f in files:
        dframes.append(f)
    return dframes


def df_and_metadata(path):
    with open(path) as f:
        metadata = []
        for line in f:
            if 'Start' not in line:
                metadata.append(line)
            else:
                column_names = line.split(';')
                column_names[-1] = column_names[-1].rstrip('\n')
                df = pd.read_csv(f, sep=';', names = column_names)
                break
    return df, metadata


def stationinfo_and_parameter(metadata):
    for i in range(len(metadata)):
        if 'Stationsnamn' in metadata[i]:
            station_info = metadata[i+1].split(';')
            station_info = ', '.join(station_info)
            station_info = station_info.lstrip('#').rstrip('\n')
            station_info = station_info.split(',')
        if 'Ämne' in metadata[i]:
            parameters = metadata[i+1].split(';')
            parameters = ', '.join(parameters)
            parameters = parameters.lstrip('#').rstrip('\n')
            parameters = parameters.split(',')
    return station_info[0].replace('Gata', ''), parameters[0].replace('PM10', 'PM$_{10}$')


def final_df(df, station, parameter):
    df_stripped = df.iloc[:, [1,2]]
    df_stripped = df_stripped.rename(columns={df_stripped.columns[0]: 'date', df_stripped.columns[1]: station + ', ' + parameter})
    df_stripped['date'] = pd.to_datetime(df_stripped['date'], format = '%Y-%m-%d %H:%M') # change time column to pandas datetime
    df_stripped = df_stripped.set_index('date') # set datetime column as index column
    return df_stripped


def df_main(path):
    """Applying all of the above functions to one directory of files"""
    df, metadata = df_and_metadata(path)
    station, parameter = stationinfo_and_parameter(metadata)
    df_final = final_df(df, parameter, station)
    return df_final

def clean_and_merge_dframes(path):
    dframes = dataframes(path)
    dframes_cleaned = [df_main(i) for i in dframes] # apply above function to all df's in dframes list
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['date'], how='outer'), dframes_cleaned) #.fillna() # merge all df's into one big
    return df_merged