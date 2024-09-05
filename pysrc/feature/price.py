import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings

root_path = "D:\\Documents\\PycharmProject\\eastmoney_data"
os.chdir(root_path)

## Pre-requisite
dirPath = "data/raw/"
tagDirPath = dirPath + "sohu_stock/"
data_date_lst = []
for filename in os.listdir(tagDirPath):
    if os.path.isdir(tagDirPath + filename):
        data_date_lst.append(datetime.strptime(filename, '%Y-%m-%d').date())

date = max(data_date_lst).strftime('%Y-%m-%d')
tag_df = pd.read_csv(tagDirPath + date + ".csv")

tag_df["stockCode"] = tag_df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()
tag_df = tag_df[~tag_df['sector'].isin(["央视50_", "AH股", "分拆预期", "破净股", "证金持股", "上证50_", "HS300_", "上证180_", "中证500", "深成500", "深证100R", "标准普尔"])]
tag_df.drop(['date'], axis=1, inplace=True)

saving = True

# Filter based on tag_df stockCode
stock_code_list = tag_df['stockCode'].drop_duplicates().to_list()

# Get the newest date of folders
priceDirPath = dirPath + "price/"
for filename in os.listdir(priceDirPath):
    data_date_lst.append(datetime.strptime(filename, '%Y-%m-%d').date())
date = max(data_date_lst).strftime('%Y-%m-%d')
priceDirPath = dirPath + "price/" + date + "/"
print(priceDirPath)

# Loading price df
print("loading raw data")
price_df_list = []
for stockCode_filename in os.listdir(priceDirPath):
    if stockCode_filename.split('.')[0] in stock_code_list:
        stock_price_df = pd.read_csv(priceDirPath + stockCode_filename, index_col=0)
        price_df_list.append(stock_price_df)
        del stock_price_df
price_df = pd.concat(price_df_list)
del price_df_list

price_df['date'] = pd.to_datetime(price_df['日期'])
price_df["stockCode"] = price_df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()
price_df['流通股数'] = price_df['成交量'] * price_df['换手率']

price_df = pd.merge(tag_df, price_df, how='outer', on='stockCode')

price_df = price_df.rename(columns={"开盘":'open','收盘':'close','成交量':'volume','成交额':'turnover',"最高":'high',"最低":'low','流通股数':'outstanding'})
print("aggregating by date,sector")
price_df = price_df.groupby(['date','sector']).agg({
        'close': lambda x: x.mean(),
        'open': lambda x: x.mean(),
        'high': lambda x: x.mean(),
        'low': lambda x: x.mean(),
        'volume': lambda x: sum(x),
        'turnover': lambda x: sum(x),
        'outstanding': lambda x: sum(x)
    })

if saving:
    print("saving")
    price_df.reset_index(inplace=True)
    price_df.to_csv('price.csv', index=False)
