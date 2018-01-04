# -*- coding:utf-8 -*-
import sys, os
import cv2
import numpy as np
import re
import time
import requests
import urllib2
import pickle
from Queue import Queue
import threading

from ImageSet import ImageSet

def dump_imageSet(imageSet):
    with  open('imageSet.pkl', 'wb') as pickle_file:
        pickle.dump(imageSet, pickle_file)

def load_imageSet():
    if not os.path.exists('imageSet.pkl'):
        imageSet = ImageSet()
    else:
        with open('imageSet.pkl', 'rb') as pickle_file:
            imageSet = pickle.load(pickle_file)
    return imageSet

def genNameToUrl(indexFileName):
    nameToUrl = {}
    indexFile = open(indexFileName)
    
    for line in indexFile.readlines():
        line = line.strip().split('\t')
        url, name = line[0], line[1]
        nameToUrl[name] = url
    indexFile.close()
    return nameToUrl

def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))



def getPictures(content):
    # patern1 = re.compile('《(.+?)》'.decode('utf-8'))
    patern = re.compile('<img src="(.+116x65.+)">'.decode('utf-8'))
    image_urls = patern.findall(content)
    return image_urls

def working(to_get_queue):
    global count, htmlpath, nameToUrl
    while not to_get_queue.empty() and count<max_page:
        filename, appid = to_get_queue.get()
        with open(os.path.join(htmlpath, filename), 'r') as f:
            content = f.read().decode('utf-8')
        image_urls = getPictures(content)
        for i in range(len(image_urls)):
            imgurl = image_urls[i].replace('116x65', '600x338')
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
                'Cookie': 'AspxAutoDetectCookieSupport=1',
            }
            request = urllib2.Request(imgurl, None, header)  
            response = urllib2.urlopen(request, timeout=60)
            imgname = "%s_%d.jpg" %(appid, i)
            with open('./tempdata/'+imgname, "wb") as f:
                f.write(response.read())
            image = cv2.imread('./tempdata/'+imgname, cv2.IMREAD_COLOR)
            imageSet.add(imgurl, image)
            os.remove('./tempdata/'+imgname)
        imageSet.addapp(appid)

        count += 1
        print "thread", int(threading.current_thread().getName()), "fetched", appid, "(%d) count" %len(image_urls), count



htmlpath = 'html/'
if len(sys.argv) < 2:
    max_page = 9999999
else:
    max_page = int(sys.argv[1])

imageSet = load_imageSet()
nameToUrl = genNameToUrl('index.txt')


htmlpath = "../steamstore/html/"
filelist = os.listdir(htmlpath)

to_get_queue = Queue()
for filename in filelist:
    store_url = nameToUrl[filename]
    appid = getID(store_url)
    if not imageSet.hasapp(appid):
        to_get_queue.put((filename, appid))
print to_get_queue.qsize(), "apps to fetch"

count = 0

NUM = 350
threads = []
for i in range(NUM):
    t = threading.Thread(target=working, name=str(i), args=(to_get_queue,))
    t.setDaemon(True)
    threads.append(t)

for t in threads:
    t.start()
for t in threads:
    t.join()


dump_imageSet(imageSet)
