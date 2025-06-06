import time
import os
import warnings

import requests
import json
from datetime import date,datetime,timedelta
import pandas as pd
from bs4 import BeautifulSoup


ID_MAP = {"个股研报": (1351846, 1603724062679),
          # "行业研报": (9934841, 1681847680985),
          }


class Scrawler:
    def __init__(self, cb_id, _id):
        self.cb_id = str(cb_id)  # 1351846
        self._id = str(_id)  # 1681842552489

        self.header = {"Connection": "keep-alive",
                       "Cookie": "qgqp_b_id=5c787bb3c7f4b8443f3a208d36f1e054; em-quote-version=topspeed; HAList=ty-0-002335-%u79D1%u534E%u6570%u636E%2Cty-1-605117-%u5FB7%u4E1A%u80A1%u4EFD%2Cty-0-000629-%u9492%u949B%u80A1%u4EFD%2Cty-0-300827-%u4E0A%u80FD%u7535%u6C14%2Cty-1-603063-%u79BE%u671B%u7535%u6C14%2Cty-0-002466-%u5929%u9F50%u9502%u4E1A%2Cty-0-002465-%u6D77%u683C%u901A%u4FE1%2Cty-1-688008-%u6F9C%u8D77%u79D1%u6280%2Ca-sh-688256-%u5BD2%u6B66%u7EAA-U%2Cty-1-603019-%u4E2D%u79D1%u66D9%u5149",
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                       "Host": "reportapi.eastmoney.com"
                       }

        self.url = 'https://reportapi.eastmoney.com/report/list?cb=datatable%s&industryCode=*&pageSize={}&industry=*&rating=&ratingChange=&beginTime={}&endTime={}&pageNo={}&fields=&qType=0&orgCode=&code=*&rcode=&p=2&pageNum=2&_=%s' % (
            cb_id, _id)

    def getHtml(self, pageSize, beginTime, endTime, pageNo):
        print(self.url.format(pageSize, beginTime, endTime, pageNo))
        response = requests.get(self.url.format(pageSize, beginTime, endTime, pageNo), headers=self.header)
        html = response.content.decode("utf-8")

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


if __name__ == "__main__":
    os.chdir("..")
    dir_path = "data/raw/"
    to_path = "data/erd/个股研报.csv"
    is_download = True
    df = pd.read_csv(to_path)

    if is_download:
        for report_type in ID_MAP:
            cb_id, _id = ID_MAP[report_type]
            scrawler = Scrawler(cb_id, _id)

            end_time = date.today()  # - timedelta(1)
            begin_time = pd.to_datetime(df['publishDate']).dt.date.max()  # date(end_time.year - 2, end_time.month, end_time.day)
            html = scrawler.getHtml(pageSize=100, beginTime=str(begin_time), endTime=str(end_time), pageNo=1)
            total_page = scrawler.format_content(html)['TotalPage']
            for page_No in range(total_page + 1):
                html = scrawler.getHtml(pageSize=100, beginTime=str(begin_time), endTime=str(end_time), pageNo=page_No)
                scrawler.saveJson(html=html, dirPath=dir_path + report_type + "/")

    # parse to csv
    for report_type in ID_MAP:
        cb_id, _id = ID_MAP[report_type]
        scrawler = Scrawler(cb_id, _id)
        html_list = scrawler.parseJson(dirPath=dir_path + report_type + "/")
        data_list = []
        for html in html_list:
            data = scrawler.format_content(html)["data"]  # dict
            data_list += data

        df = pd.DataFrame(data_list)

        df["link"] = "https://data.eastmoney.com/report/zw_industry.jshtml?encodeUrl=" + df["encodeUrl"]
        # df["main_text"] = df["link"].apply(f)

        df.to_csv(to_path, index=False)
