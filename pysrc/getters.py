import json

from .utils import *

ROOT_PATH = "D:/Documents/PycharmProject/eastmoney_data/"
DATA_PATH = ROOT_PATH + "data/"
PRICE_PATH = getLatestDateDirPath(DATA_PATH + "raw/price/")
TAG_PATH = DATA_PATH + "raw/sohu_stock/"


# ==================== price ====================
def parseRawPrice(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df['日期'])
    df["stockCode"] = df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()
    df['流通股数'] = df['成交量'] * df['换手率']
    return df


def getRawPriceByStockCode(code: str):
    df = pd.read_csv(PRICE_PATH + "/" + code + ".csv", index_col=0)
    return df


def getPriceByStockCode(code: str):
    df = getRawPriceByStockCode(code)
    df = parseRawPrice(df)
    return df


# ==================== sector ====================
def parseRawSector(df: pd.DataFrame):
    df["stockCode"] = df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()
    df = df[~df['sector'].isin(
        ["央视50_", "AH股", "分拆预期", "破净股", "证金持股", "上证50_", "HS300_", "上证180_", "中证500", "深成500", "深证100R", "标准普尔"])]
    df = df.drop(['date'], axis=1)
    return df


def getRawSector():
    date = getLatestDateDir(TAG_PATH)
    df = pd.read_csv(TAG_PATH + date + ".csv")
    return df


def getSector():
    df = getRawSector()
    df = parseRawSector(df)
    return df


# ==================== rating ====================
def parseRating(df):
    df["stockCode"] = df['stockCode'].astype("str").apply(lambda x: x.zfill(6)).to_list()
    df['publishDate'] = pd.to_datetime(df['publishDate'])
    df = df.drop_duplicates()
    return df


def getRawRating(full: bool = False):
    df = pd.read_csv(DATA_PATH + "erd/个股研报.csv")
    if not full:
        df = df[["publishDate", "stockCode", "orgSName", "emRatingValue", "emRatingName"]].sort_values("publishDate")
    return df


def getRating(full: bool = False):
    df = getRawRating(full)
    df = parseRating(df)
    return df


# ==================== test ====================
def __main():
    df = getPriceByStockCode("000001")
    print(df)
    print(df.columns)
    df = getSector()
    print(df)
    print(df.columns)
    df = getRating(full=False)
    print(df)
    print(df.columns)


if __name__ == "__main__":
    __main()
