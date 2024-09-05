import json
import time
import random
import requests
from bs4 import BeautifulSoup, NavigableString
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
import re
import pyodbc


class AiTest:
    def __init__(self):
        self.tongyi_url = 'https://qianwen.biz.aliyun.com/dialog/conversation'
        self.headers = 1
    def get_tongyi_answer(self):
        response = requests.post(self.tongyi_url, data=json.dumps(payload), headers=self.headers)
        print(1)

    def calculate(self):
        self.get_tongyi_answer()
        print(1)


def main():
    obj = AiTest()
    obj.calculate()


if __name__ == '__main__':
    main()
