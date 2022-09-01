import numpy as np
import pandas as pd
import sklearn

# read in data
df_NO2 = pd.read_csv('/content/drive/MyDrive/Thesis/NO2/NO2_all_stations_cleaned.csv')
df_NO2['date'] = pd.to_datetime(df_NO2['date'], format = '%Y-%m-%d %H:%M') # change time column to pandas datetime
df_NO2 = df_NO2.set_index('date') # date column as index

df_weather = pd.read_csv('/content/drive/MyDrive/Thesis/NO2/metdata.csv')
df_weather['date'] = pd.to_datetime(df_weather['date'], format = '%Y-%m-%d %H:%M') # change time column to pandas datetime
df_weather = df_weather.set_index('date') # date column as index

# replace zero and negative with NaNs and interpolate data
df_NO2[df_NO2 <= 0] = np.NaN
df_NO2.interpolate(inplace=True)

# split into train, val, and test sets
df_NO2_train = df_NO2['2016-01-01 00:00':'2019-01-01 00:00']
df_NO2_val = df_NO2['2019-01-01 01:00:00':'2020-01-01 00:00:00']
df_NO2_test = df_NO2['2021-01-25 16:00:00':]

df_weather_train = df_weather['2016-01-01 00:00':'2019-01-01 00:00']
df_weather_val = df_weather['2019-01-01 01:00:00':'2020-01-01 00:00:00']
df_weather_test = df_weather['2021-01-25 16:00:00':]


# index needed later
index_train = df_NO2_train.index 
index_val = df_NO2_val.index
index_test = df_NO2_test.index


df_train = df_NO2_train.merge(df_weather_train, on='date')
df_val = df_NO2_val.merge(df_weather_val, on='date')
df_test = df_NO2_test.merge(df_weather_test, on='date')


# input variables used in robust regression model
stations = ['NO$_2$, Stockholm Torkel Knutssonsgatan',
            'NO$_2$, Stockholm Hornsgatan 108 ',
            'NO$_2$, Stockholm Sveavägen 59 ',
            'NO$_2$, Stockholm E4/E20 Lilla Essingen',
            'Temperature', 
            'Relative humidity', 
            'Precipitation', 
            'Solar radiation',
            'Wind speed',
            'Sine day', 
            'Cosine day']
          

# create y and X matrix for train, val, and test sets
y_train = df_train['NO$_2$, Stockholm Torkel Knutssonsgatan']
X_train = df_train[stations]

y_val = df_val['NO$_2$, Stockholm Torkel Knutssonsgatan']
X_val = df_val[stations]

y_test = df_test['NO$_2$, Stockholm Torkel Knutssonsgatan']
X_test = df_test[stations]


from sklearn.preprocessing import MinMaxScaler
# two scalers, one for X and on for y
scaler1 = MinMaxScaler() 
scaler2 = MinMaxScaler()

# normalize train set
X_train = scaler1.fit_transform(X_train)
X_train = pd.DataFrame(X_train, columns=stations)
X_train.insert(0, 'date', index_train)
X_train.set_index('date', inplace=True)

y_train = scaler2.fit_transform(y_train.to_frame())
y_train = pd.DataFrame(y_train, columns = ['NO$_2$, Torkel Knutssonsgatan'])
y_train.insert(0, 'date', index_train)
y_train.set_index('date', inplace=True)

# normalize validation set
X_val = scaler1.transform(X_val) # fit is not used here to only use statistics from train data
X_val = pd.DataFrame(X_val, columns=stations)
X_val.insert(0, 'date', index_val)
X_val.set_index('date', inplace=True)

y_val = scaler2.transform(y_val.to_frame())
y_val = pd.DataFrame(y_val, columns = ['NO$_2$, Torkel Knutssonsgatan'])
y_val.insert(0, 'date', index_val)
y_val.set_index('date', inplace=True)

# normalize test set
X_test = scaler1.transform(X_test) # not fit here to use statistics from train data
X_test = pd.DataFrame(X_test, columns=stations)
X_test.insert(0, 'date', index_test)
X_test.set_index('date', inplace=True)

y_test = scaler2.transform(y_test.to_frame()) 
y_test = pd.DataFrame(y_test, columns = ['NO$_2$, Torkel Knutssonsgatan'])
y_test.insert(0, 'date', index_test)
y_test.set_index('date', inplace=True)
