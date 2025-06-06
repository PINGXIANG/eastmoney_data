import pandas as pd
import numpy as np
from getters import *


def fill_missing_dates(group, valid_dates: list):
    # Generate the full date range for this specific stockCode
    min_date = group['date'].min()
    max_date = group['date'].max()
    stock_valid_dates = valid_dates[(valid_dates >= min_date) & (valid_dates <= max_date)]

    # Reindex the group DataFrame to fill in missing dates
    group = group.set_index('date').reindex(stock_valid_dates).sort_values("date").ffill()

    # Restore the stockCode and date columns
    group = group.reset_index().rename(columns={'index': 'date'})
    return group


def shift_to_next_valid_date(row, valid_dates: list):
    # Find the index of the publishDate in the valid_dates array
    idx = np.searchsorted(valid_dates, row['publishDate'], side='left') - 1  # Find where this publishDate fits in valid_dates
    if idx < len(valid_dates):  # Ensure we don't go out of bounds
        return valid_dates[idx]  # Shift to the next valid date
    else:
        return np.nan  # If no valid date after publishDate, return NaN


# ==================== univ ====================
def genUniv():
    # sector
    print("loading sector_df")
    sector_df = getSector()
    stock_code_list = sector_df['stockCode'].drop_duplicates().to_list()
    # rating
    print("loading rating_df")
    rating_df = getRating()
    # price
    print("loading all price_df")
    price_df_list = []
    for stock_code in stock_code_list:
        try:
            stock_price_df = getPriceByStockCode(stock_code)
            price_df_list.append(stock_price_df)
            del stock_price_df
        except FileNotFoundError:
            print(FileNotFoundError, stock_code, "not found")
    df = pd.concat(price_df_list)
    # fill missing date for certain stockCode
    print("filling missing date using prev date")
    print("raw (date,stockCode) pairs: ", len(df[['stockCode', 'date']].drop_duplicates()))
    df = df.groupby('stockCode').apply(fill_missing_dates, valid_dates=df['date'].unique())
    df = df.reset_index(drop=True)
    print("current (date,stockCode) pairs: ", len(df[['stockCode', 'date']].drop_duplicates()))
    # left join
    # rating
    valid_dates = df['date'].unique()
    rating_dates = rating_df['publishDate'].unique()
    rating_df = rating_df[(rating_df['publishDate'] > rating_dates[rating_dates < valid_dates.min()].max()) & (rating_df['publishDate'] < valid_dates.max())]
    rating_df['date'] = rating_df.apply(shift_to_next_valid_date, valid_dates=valid_dates, axis=1)
    rating_df = rating_df.groupby(['date', 'stockCode']).agg(
        avgRatingValue=('emRatingValue', 'mean'),
        ratingCnt=('orgSName', 'count')
    ).reset_index()
    df = pd.merge(df, rating_df[['date', 'stockCode', 'avgRatingValue', 'ratingCnt']], how="left", on=['date', 'stockCode'])
    df['ratingCnt'] = df['ratingCnt'].fillna(0).astype(int)
    # sector
    df = pd.merge(df, sector_df, how='left', on='stockCode')
    df = df.drop_duplicates()
    return df


# ==================== signal ====================


# ==================== test ====================
def __main():
    df = genUniv()
    print(df)
    print(df.columns)
    df.to_csv(DATA_PATH + "erd/price.csv")


if __name__ == "__main__":
    __main()
