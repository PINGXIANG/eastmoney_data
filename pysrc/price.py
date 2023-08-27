import logging
import time

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
import os
import sys

warnings.simplefilter(action='ignore', category=FutureWarning)

# DEFAULT DATE STRING
LAST_WEEK = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')
LAST_YEAR = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
LAST_3YEARS = (datetime.today() - timedelta(days=365 * 3)).strftime('%Y%m%d')
TODAY = datetime.today().strftime('%Y%m%d')


# ---- inner function ----
def maxProfit(prices: list) -> int:
    pnl = 0
    min_price = prices[0]

    for i in range(1, len(prices)):
        if prices[i] < prices[i - 1]:
            min_price = min(min_price, prices[i])

        pnl = max(pnl, prices[i] - min_price)
    return pnl


# Set up logging files
logPath = "../logs/" + os.path.basename(__file__).split(".")[0] + "/"
if not os.path.exists(logPath):
    os.makedirs(logPath)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=f'{logPath + datetime.today().strftime("%Y%m%d")}.log', filemode='w')

# Get stock code list
dirPath = "../data/raw/"
tagDirPath = dirPath + "sohu_stock/"
data_date_lst = []
for filename in os.listdir(tagDirPath):
    if os.path.isdir(tagDirPath + filename):
        data_date_lst.append(datetime.strptime(filename, '%Y-%m-%d').date())
date = max(data_date_lst).strftime('%Y-%m-%d')
tag_df = pd.read_csv(tagDirPath + date + ".csv")
stock_code_lst = tag_df['stockCode'].drop_duplicates().astype("str").apply(lambda x: x.zfill(6)).to_list()


priceDirPath = dirPath + "price/" + datetime.today().strftime('%Y-%m-%d') + "/"
if not os.path.exists(priceDirPath):
    os.makedirs(priceDirPath)

checkpoint = True
if checkpoint:
    done = set([filename.split('.')[0] for filename in os.listdir(priceDirPath)])
    stock_code_lst = list(set(stock_code_lst) - done)


for stock_code in stock_code_lst:
    try:
        data = ak.stock_zh_a_hist(symbol=str(stock_code), period="daily", start_date=LAST_3YEARS, end_date=TODAY, adjust="qfq")
        data['stockCode'] = str(stock_code)
        data.to_csv(f"{priceDirPath+str(stock_code)}.csv")
        print(str(stock_code), "Done.")
        del data
    except Exception as e:
        print(str(stock_code), "Failed.")
        logger.fatal(f"{str(stock_code)}: downloading failed with error - {str(e)}")

    time.sleep(1)
