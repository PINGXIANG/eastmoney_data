import pandas as pd


def feature_engineering(data: pd.DataFrame):
    # Convert 'date' column to datetime if not already. Sort the data by 'sector' and 'date'
    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by=['sector', 'date'], inplace=True)
    
    # Create lagged features
    lag_periods = [1, 5, 10]  # Number of lag periods
    for lag in lag_periods:
        for col in ['open', 'close', 'volume', 'turnover', 'outstanding', 'high', 'low']:
            data[f'{col}_lag_{lag}'] = data.groupby('sector')[col].shift(lag)

    # Reset the index to separate 'sector' from the index
    data.reset_index(level='sector', inplace=True)
    # Create moving averages
    moving_averages = [5, 10, 20]  # Moving average periods
    for ma in moving_averages:
        for col in ['open', 'close', 'volume', 'turnover', 'outstanding', 'high', 'low']:
            data[f'{col}_ma_{ma}'] = data.groupby('sector')[col].rolling(window=ma).mean().reset_index(level='sector',
                                                                                                       drop=True)

    # Calculate price change features
    data['price_change'] = data.groupby('sector')['close'].diff()

    # Calculate log return features
    data['log_return_lag_1'] = data.groupby('sector')['log_return'].shift(1)

    # Calculate relative indicators
    data['return_vs_lag'] = data['log_return'] - data['log_return_lag_1']
    data['return_vs_ma_5'] = data['log_return'] - data['close_ma_5']
    data['return_vs_ma_10'] = data['log_return'] - data['close_ma_10']

    # Define features and target
    features = ['open', 'close', 'volume', 'turnover', 'outstanding', 'high', 'low', 'log_return']
    # Number of lag periods
    lag_periods = [1, 2, 5]  # You can adjust this list

    # Initialize an empty DataFrame to store the new features
    new_features = pd.DataFrame(index=data.index)

    # Loop through each lag period
    for lag in lag_periods:
        for feature in features:
            # Create cross-lagged feature
            cross_lagged_feature = data.groupby('sector')[feature].shift(-lag)
            new_feature_name = f'{feature}_lag_{lag}'

            # Add the cross-lagged feature to the new_features DataFrame
            new_features[new_feature_name] = cross_lagged_feature

    # Combine the new_features DataFrame with the original data
    data = pd.concat([data, new_features], axis=1)

    # Drop rows with NaN due to feature engineering
    data.dropna(inplace=True)

    return data


def summary(df):
    print(f'data shape: {df.shape}')
    summ = pd.DataFrame(df.dtypes, columns=['data type'])
    summ['#missing'] = df.isnull().sum().values
    summ['%missing'] = df.isnull().sum().values / len(df) * 100
    summ['#unique'] = df.nunique().values
    desc = pd.DataFrame(df.describe(include='all').transpose())
    summ['min'] = desc['min'].values
    summ['max'] = desc['max'].values
    summ['first value'] = df.loc[0].values
    summ['second value'] = df.loc[1].values
    summ['third value'] = df.loc[2].values

    return summ