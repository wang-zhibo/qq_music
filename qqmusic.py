#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author : zhibo.wang
# E-mail : d_1206@qq.com
# Date   : 18/11/25 23:39:11
# Desc   : qq音乐 林俊杰-雪落下的声音 评论

import time
import json
import random
import pymongo
import requests


config = {
    'HOST': '127.0.0.1',
    'PORT': 27017,
    'DB': 'wangzhibo',
}

def mongo_con_keepalive(confing=config):
    conn = pymongo.MongoClient(confing['HOST'], confing['PORT'])
    conn = conn[confing['DB']]
    if confing.get('USER'):
        conn.authenticate(confing['USER'], confing['PASSWORD'])
    return conn


class Crawl():
    start_url = "https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=798799166&loginUin=1152921504630904742&hostUin=0&format=json&inCharset=GB2312&outCharset=GB2312&notice=0&platform=jqspaframe.json&needNewCode=0&cid=205360772&reqtype=2&biztype=1&topid=219004455&cmd=8&needmusiccrit=0&pagenum=1&pagesize=25&domain=qq.com&ct=6&cv=50600"
    time_out = 10

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) patch/0 QQMusic/5.6.0 Released[1]",
        "Referer": "https://y.qq.com/musicmac/v4/song/detail.html?songid=219004455&songtype=13",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Host": "c.y.qq.com",
        "Origin": "https://y.qq.com",
    }
    insert_table = "qq_music_comment"
    proxyMeta = "http://H4O6Y9PI266660WD:0A604C09CDF7BED6@proxy.abuyun.com:9020"
    proxies = {
                "http": proxyMeta,
                "https": proxyMeta,
              }
    is_proxy = True
    if is_proxy:
        wait_time = [0.25, 0.26, 0.27]
    else:
        wait_time = [1, 1.1, 1.2, 1.3]     # 间隔时间

    def __init__(self):
        self.db = mongo_con_keepalive()

    def req(self, url):
        soup = None
        try:
            if self.is_proxy:
                r = requests.get(url, headers=self.headers, timeout=self.time_out, proxies=self.proxies)
            else:
                r = requests.get(url, headers=self.headers, timeout=self.time_out)
            if r.status_code == 200:
                soup = r.json()
        except Exception as e:
            print("req error: ", e)
        return soup

    def create_pages(self, soup):
        pages = None
        try:
            count = soup.get("comment").get("commenttotal")
            pages = list(range(2, len(list(range(0, count, 25))) +1 ))
        except:
            pass
        return pages

    def get_time_stamp(self):
        # 生成时间戳
        return str(int(time.time()))

    def create_lasthotcommentid(self):
        #return "&lasthotcommentid=song_219004455_3394972532_{0}".format(self.get_time_stamp())
        return ""

    def run(self):
        index_url = "{0}{1}".format(
            self.start_url,
            self.create_lasthotcommentid()
        )
        data_index = self.req(index_url)
        if data_index:
            if data_index.get("code") == 0:
                end_data_index = data_index.get("comment").get("commentlist")
                self.db.get_collection(self.insert_table).insert_many(end_data_index)
                pages = self.create_pages(data_index)
                if pages:
                    for page in pages:
                        url_ = "{0}&pagenum={1}".format(self.start_url.replace("&pagenum=1", ""), page)
                        url = "{0}{1}".format(url_, self.create_lasthotcommentid())

                        print(url)
                        data = self.req(url)
                        if data:
                            if data.get("code") == 0:
                                end_data = data.get("comment").get("commentlist")
                                self.db.get_collection(self.insert_table).insert_many(end_data)
                        time.sleep(random.choice(self.wait_time))


if __name__ == "__main__":
    C = Crawl()
    C.run()

