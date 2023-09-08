# coding: utf-8
import json
from requests import Session
import settings
from settings import logger


HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh;q=0.5',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Origin': 'https://idp.vetrf.ru',
    'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="106", "Google Chrome";v="106"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

class BaseSession(Session):

    def __init__(self, cookies):
        super().__init__()
        self.headers = HEADERS
        self.cookies.update(cookies)

    def fetch(self, url, data=None, *args, **kwargs):
        if data is None:
            return self.get(url, *args, **kwargs)
        else:
            return self.post(url, data=data, *args, **kwargs)
