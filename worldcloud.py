#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author : zhibo.wang
# E-mail : d_1206@qq.com
# Date   : 18/11/26 00:53:22
# Desc   :

import re
import os
import jieba
import fool
import codecs
import pymongo
from scipy.misc import imread
from wordcloud import WordCloud
from matplotlib import pyplot as plt

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

"""
emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)
"""
emoji_pattern = re.compile(
    '[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+')

def remove_emoji(text):
    return emoji_pattern.sub(r'', text)

def draw_wordcloud(comment_text, fenci):
    comment_text = remove_emoji(comment_text)
    if fenci == "jieba":
        cut_text = " ".join(jieba.cut(comment_text))
    else:
        dd = fool.cut(comment_text)
        cut_text = " ".join(fool.cut(comment_text)[0])
    color_mask = imread('/Users/work/Downloads/e0f057b7a1a61de962d89347b6d7201f-d4o1tzm.jpg')
    font = r'/Users/work/Downloads/simfang.ttf'
    stopwords = open("stopworld.txt").read().split("\n")
    cloud = WordCloud(
        font_path=font,
        background_color='white',
        max_words=20000,
        max_font_size=400,
        min_font_size=10,
        mask=color_mask,
        stopwords=stopwords,
    )

    word_cloud = cloud.generate(cut_text)
    word_cloud.to_file('{0}.jpg'.format(fenci))

def run():
    fenci_list = ["jieba", "fool"]
    db = mongo_con_keepalive()
    datas = db.get_collection("qq_music_comment").find({})
    print("count: ", datas.count())
    comment_text = "".join([i.get("rootcommentcontent").strip() for i in datas if i.get("rootcommentcontent")])
    for fenci in fenci_list:
        print(fenci)
        draw_wordcloud(comment_text, fenci)


if __name__ == "__main__":
    run()

