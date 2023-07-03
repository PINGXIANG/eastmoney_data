import time
import os
import warnings

import requests
import json
from datetime import date,datetime
import pandas as pd
from bs4 import BeautifulSoup
import re
import ast

ID_MAP = {"个股研报": (1351846, 1603724062679),
          "行业研报": (9934841, 1681847680985),
          }


class Scrawler:
    def __init__(self):
        self.url = 'https://q.stock.sohu.com/cn/bk_6578.shtml'

    def getHtml(self, url):
        print(url)
        response = requests.get(url)

        html = response.content.decode("gbk")

        return html

    @staticmethod
    def saveJson(html, dirPath):
        n = len(os.listdir(dirPath))
        with open(dirPath + "%s.json" % str(n + 1), "w") as file:
            json.dump(html, file, indent=6)

    def format_content(self, content):
        if len(content):
            content = content.replace('datatable%s(' % self.cb_id, '')[:-1]
            return json.loads(content)
        else:
            return None

    @staticmethod
    def parseJson(dirPath):
        html_list = []
        for filename in os.listdir(dirPath):
            with open(dirPath + filename, "r") as file:
                html = json.loads(file.read())
            html_list.append(html)
        return list(set(html_list))


# TODO
def f(url):
    header = {"Connection": "keep-alive",
              "Cookie": "qgqp_b_id=5c787bb3c7f4b8443f3a208d36f1e054; qRecords=%5B%7B%22name%22%3A%22%u76DF%u79D1%u836F%u4E1A-U%22%2C%22code%22%3A%22SH688373%22%7D%2C%7B%22name%22%3A%22%u8302%u4E1A%u5546%u4E1A%22%2C%22code%22%3A%22SH600828%22%7D%5D; em-quote-version=topspeed; HAList=ty-0-002335-%u79D1%u534E%u6570%u636E%2Cty-1-605117-%u5FB7%u4E1A%u80A1%u4EFD%2Cty-0-000629-%u9492%u949B%u80A1%u4EFD%2Cty-0-300827-%u4E0A%u80FD%u7535%u6C14%2Cty-1-603063-%u79BE%u671B%u7535%u6C14%2Cty-0-002466-%u5929%u9F50%u9502%u4E1A%2Cty-0-002465-%u6D77%u683C%u901A%u4FE1%2Cty-1-688008-%u6F9C%u8D77%u79D1%u6280%2Ca-sh-688256-%u5BD2%u6B66%u7EAA-U%2Cty-1-603019-%u4E2D%u79D1%u66D9%u5149",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
              "Host": "data.eastmoney.com"
              }
    response = requests.get(url, headers=header)
    html = response.content.decode("utf-8")
    # with open("main.json", "w") as file:
    #     json.dump(html, file, indent=6)
    main_text = BeautifulSoup(html, "html.parser").body.find('div', attrs={'class': 'ctx-box'}).text

    return main_text


if __name__ == "__main__":
    os.chdir("..")
    dir_path = "data/raw/sohu_stock/"
    is_download = True

    if is_download:
        today = str(date.today())
        scrawler = Scrawler()
        html = scrawler.getHtml(url="https://hq.stock.sohu.com/pl/pl-1.html")

        s = "[".join(html.split('[')[1:])
        table = [ast.literal_eval(e)[:3] for e in re.findall(r"\[.*?\]", s)]

        for sector_id,sector,sector_cnt in table:
            if os.path.exists(f"{dir_path+today}/{sector}.csv"):
                continue
            df = pd.read_html("https://q.stock.sohu.com/cn/bk_%s.shtml" % sector_id, encoding="gbk")[0]
            df = df.rename(columns={"股票代码点击按代码排序查询": "stockCode", "股票名称": "stockName"})[["stockCode", "stockName"]]
            sector = sector.replace("/","-")
            df["sector"] = sector
            df["sectorCount"] = sector_cnt
            df['date'] = today
            if not os.path.exists(dir_path + today):
                os.makedirs(dir_path + today)
            df.to_csv(f"{dir_path+today}/{sector}.csv", index=False)

    date_list = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    d = str(max([date.fromisoformat(d) for d in date_list]))
    df_list = [pd.read_csv(dir_path+d + '/' + filename) for filename in os.listdir(dir_path+d)]
    df = pd.concat(df_list)
    df.to_csv(f"{dir_path}{d}.csv", index=False)

