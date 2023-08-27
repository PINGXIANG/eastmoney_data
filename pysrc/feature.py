import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
import warnings

os.chdir(sys.path[0] + "\\..")


#  Rating
rating_df = pd.read_csv("个股研报.csv")
rating_df['publishDate'] = pd.to_datetime(rating_df['publishDate']).dt.strftime('%Y-%m-%d')
rating_df["stockCode"] = rating_df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()

