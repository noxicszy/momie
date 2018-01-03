# -*- coding:utf-8 -*-
import requests, json
import os, sys
import re, time
from Queue import Queue
import threading
import string
from bs4 import BeautifulSoup

def genNameToUrl(indexFileName):
    nameToUrl = {}
    indexFile = open(indexFileName)
    
    for line in indexFile.readlines():
        line = line.strip().split('\t')
        url, name = line[0], line[1]
        nameToUrl[name] = url
    indexFile.close()
    return nameToUrl



def isapp(url):
    return ("http://store.steampowered.com/app/" in url)

def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))

def getENName(store_url):
    try:
        m = re.search("app/\d+/(.*)/", store_url)
        return str(m.group(1))
    except Exception,e:
        print store_url, "has raise an Exception",e
        return 'None'

def getStoreName(content):
    m = re.search("<div class=\"apphub_AppName\">(.+)</div>", content)
    return m.group(1)

def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))

def valid_searchname(storeName):
    valid_chars = "-_.():&,\' %s%s" % (string.ascii_letters, string.digits)
    invalid_chars = ';™+–®°“”*!é[]/\#<>’²"•★|`～「″☆」‘！^／√❌＋ᵠ🍉†＜＞'.decode('utf-8')
    searchName = ''.join(c for c in storeName if c not in invalid_chars)
    return searchName.encode('utf-8')


if __name__ == '__main__':
    nameToUrl = genNameToUrl('index.txt')
    htmlpath = '../steamstore/html/'
    # htmlpath = 'testhtml'
    htmllist =  os.listdir(htmlpath)

    namefname = 'app_name.txt'

    length = len(htmllist)
    inavailable = []
    id_name_list = []
    for i in range(length):
        if i % 100 == 0:
            print "processing {}/{}".format(i, length)

        filename = htmllist[i]
        url = nameToUrl[filename]

        if isapp(url):
            appid = getID(url)
        else:
            inavailable.append((filename, url))
            continue

        with open(os.path.join(htmlpath, filename), 'r') as f:
            content = f.read().decode('utf-8')
        

        try:
            # soup = BeautifulSoup(content, "html.parser")
            # storeName = soup.find('div',{'class': 'apphub_AppName'}).string
            storeName = getStoreName(content)
        except:
            inavailable.append((filename, url))
            continue

        searchName = valid_searchname(storeName)
        id_name_list.append((appid, searchName))




    with open(namefname, 'w') as f:
        for appid, searchName in id_name_list:
            f.write('{}\t{}\n'.format(appid, searchName))


    print '{} names is not available'.format(len(inavailable))
    with open('todelete.txt', 'w') as f:
        for filename,url in inavailable:
            f.write(url+'\n')
            os.remove(os.path.join(htmlpath, filename))

