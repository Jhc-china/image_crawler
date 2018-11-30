#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 17:07:47 2018

@author: jhc
"""

import os
import math
import argparse
import requests
import re

version = 'Image Crawler Version 1.0'

engine_list = ('baidu', 'google')

batch_size = 50

image_dir = '/home/jhc/Project/Python/crawler/images/'

raw_baidu_url = r'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&word={word}&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&cg=girl&pn={pageNum}&rn={eachNum}&gsm=1e00000000001e&1490169411926='

help_describe = '''
    Image crawler to download images. version: 1.0
'''

help_end = '''
    Author: JiangHaochen
    E-mail: hcingjhon@gmail.com
'''

class img:
    className = ''
    idx = 0
    thumbURL = ''
    objURL = ''
    width = 0
    height = 0
    imgtype = ''
    
    def __init__(self, name, i, tU, oU, w, h, t):
        self.className = name
        self.idx = i
        self.thumbURL = tU
        self.objURL = oU
        self.width = w
        self.height = h
        self.imgtype = t
    
    def __str__(self):
        s = "({" + "'index': {0}, 'thumbURL': '{1}', 'objURL': '{2}', 'width': {3}, 'height': {4}, 'imgtype': '{5}'".format(self.idx, self.thumbURL, self.objURL, self.width, self.height, self.imgtype) + "})"
        return s
    
    def download_thumb(self):
        pass
        
    def download_obj(self):
        try:
            pic = requests.get(self.objURL, timeout=10)
        except requests.exceptions.ConnectionError:
            print('image cannot download')
        
        dir = image_dir + '/' + self.className +'/' + self.className + '_' + str(self.idx) + '.' + self.imgtype
        
        try:
            fs = open(dir, 'wb')
            fs.write(pic.content)
        except IOError:
            print('open file failed or no such file')
        else:
            print('Succesfully download image {}-{}. width {}, heigth: {}'.format(self.className, self.idx, self.width, self.height))
            fs.close()
        
def _init_cmd() :
    cmd_parse = argparse.ArgumentParser(description=help_describe, epilog=help_end)
    cmd_group = cmd_parse.add_mutually_exclusive_group()
    cmd_group.add_argument('-v', '--version', action='store_true', help='show the crawler version')
    cmd_parse.add_argument('-e', '--engine', type=str, dest='engine', help='choose the search engine. Default: baidu', default='baidu')
    cmd_parse.add_argument('-w', '--word', type=str, dest='word', help='choose the keyword to search. Default: \'\', if multiple input, please use , to split, like a,b', default='')
    cmd_parse.add_argument('-n', '--number', type=int, dest='number', help='choose the number of images. Default: 100', default=100)
    args = cmd_parse.parse_args()
    if args.version:
        print(version)
    else:
        if args.engine.lower() in engine_list and args.word != '' and args.number > 0:
            __engine = args.engine.lower()
            __word = args.word
            __number = args.number
            return __engine, __word, __number
        elif args.word == '':
            print('Please input the searching word')
        elif args.number <= 0:
            print('Please input the right number (>0)')
        else:
            print('The engine should be one of {}'.format(engine_list))

def _get_html(url):
    response = requests.get(url)
    html_text = response.text
    #html_text = response.content.decode('UTF-8')
    return html_text

def _baidu_decode(url):
    c = ['_z2C$q', '_z&e3B', 'AzdH3F']
    d = {'w':'a', 'k':'b', 'v':'c', '1':'d', 'j':'e', 'u':'f', '2':'g', 'i':'h', 't':'i', '3':'j', 'h':'k', 's':'l', '4':'m', 'g':'n', '5':'o', 'r':'p', 'q':'q', '6':'r', 'f':'s', 'p':'t', '7':'u', 'e':'v', 'o':'w', '8':'1', 'd':'2', 'n':'3', '9':'4', 'c':'5', 'm':'6', '0':'7', 'b':'8', 'l':'9', 'a':'0', '_z2C$q':':', '_z&e3B':'.', 'AzdH3F':'/'}
    
    if url == None or 'http' in url:
        print('Not baidu encode url')
        return url
    raw_url = url
    res = ''
    for m in c:
        raw_url = raw_url.replace(m,d[m])
    for char in raw_url:
        if re.match('^[a-w\d]+$',char):
            char = d[char]
        res = res + char
    return res

def _baidu_search(html):
    pic_thumb_url = re.findall('"thumbURL":"(.*?)",', html, re.S)
    pic_encode_url = re.findall('"objURL":"(.*?)",', html, re.S)
    pic_width = re.findall('"width":(\d+?),', html, re.S)
    pic_height = re.findall('"height":(\d+?),', html, re.S)
    pic_type = re.findall('"type":"(.*?)",', html, re.S)
    return pic_thumb_url, pic_encode_url, pic_width, pic_height, pic_type

def main():
    try:
        engine, word, number = _init_cmd()
    except TypeError:
        return
    word_list = word.split(',')
    for wordi in word_list:
        word_dir = image_dir + '/' + wordi + '/'
        if not os.path.exists(word_dir):
            os.mkdir(word_dir)
        if engine.lower() == 'baidu':
            total_page = math.ceil(number/batch_size)
            last_num = number%batch_size
            page = 1
            images = []
            while(page <= total_page):
                if page == total_page and last_num != 0:
                    url = raw_baidu_url.format(word=wordi, pageNum=page, eachNum=last_num)
                    try:
                        imgset_html = _get_html(url)
                    except TypeError:
                        print('HTML content error')
                        return
                    thumb_url, encode_url, width, height, endfix = _baidu_search(imgset_html)
                    for idx in range(len(encode_url)):
                        pic_url = _baidu_decode(encode_url[idx])
                        imgi = img(wordi, (page-1)*batch_size+idx+1, thumb_url[idx], pic_url, int(width[idx]), int(height[idx]), endfix[idx])
                        images.append(imgi)
                    page = page + 1
                    continue
                url = raw_baidu_url.format(word=wordi, pageNum=page, eachNum=batch_size)
                try:
                    imgset_html = _get_html(url)
                except TypeError:
                    print('HTML content error')
                    return
                thumb_url, encode_url, width, height, endfix = _baidu_search(imgset_html)
                for idx in range(len(encode_url)):
                    pic_url = _baidu_decode(encode_url[idx])
                    imgi = img(wordi, (page-1)*batch_size+idx+1, thumb_url[idx], pic_url, int(width[idx]), int(height[idx]), endfix[idx])
                    images.append(imgi)
                page = page + 1
        for idx in range(len(images)):
            images[idx].download_obj()
    

if __name__ == '__main__':
    main()