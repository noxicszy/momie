# -*- coding:utf-8 -*-
import requests, json
import os, sys
import re, time
# from Queue import Queue
import threading

def is_chinese(uchar):
    """verify if an unicode is chines"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def findZHName(content):
    patern1 = re.compile('《(.+?)》'.decode('utf-8'))
    patern2 = re.compile('「(.+?)」'.decode('utf-8'))
    names = patern1.findall(content)+patern2.findall(content)

    for i in range(len(names)):
        
        names[i] = ''.join(names[i].split('</em>'))
        names[i] = ''.join(names[i].split('<em>'))
        names[i] = ''.join([c for c in names[i] if is_chinese(c)])
    names = [x for x in names if x!= '']
    return names


baidu_folder = 'baidu_result/'
baidulist = os.listdir(baidu_folder)[:10]

for i in range(len(baidulist)):
    appid = baidulist[i]
    zhName = {}
    apppath = os.path.join(baidu_folder, appid)
    htmllist = os.listdir(apppath)
    for filename in htmllist:
        with open(os.path.join(apppath, filename), 'r') as f:
            content = f.read().decode('utf-8')
            names = findZHName(content)
            

            for name in names:
                if name in zhName:
                    zhName[name] += 1
                else:
                    zhName[name] = 1

    items = zhName.items()
    items = sorted(items, lambda x, y: cmp(x[1], y[1]), reverse=True)
    for key, value in items:
        print appid, key, value
    print 
# apppath = 'baidu_result/71240/'
# filename = '1.html'
# with open(os.path.join(apppath, filename), 'r') as f:
#     content = f.read().decode('utf-8')
# names = findZHName(content)
# for name in names:
#     print name