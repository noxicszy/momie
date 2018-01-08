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

def working(to_get_queue):
    global count, imagepath
    # while not to_get_queue.empty() and count<max_page:
        # appid = to_get_queue.get()
        # apppath = os.path.join(imagepath, appid)
        # filelist = os.listdir(apppath)
        # for imagename in filelist:
        #     image = cv2.imread(os.path.join(apppath, imagename), cv2.IMREAD_COLOR)
        #     imgurl = imgToUrl[imagename]
        #     imageSet.add(imgurl, image)
        # imageSet.addapp(appid)

        # count += 1
        # print "thread", int(threading.current_thread().getName()), "fetched", appid, "count", count


if len(sys.argv) < 2:
    max_page = 9999999
else:
    max_page = int(sys.argv[1])

imageSet = ImageSet()
nameToUrl = genNameToUrl('index.txt')
imgToUrl = genNameToUrl('image_index.txt')

imagepath = 'images'
imagelist = os.listdir(imagepath)

with open('appidlist.pkl', 'rb') as f:
    applist = pickle.load(f)


to_get = []
for appid in imagelist:
    if not imageSet.hasapp(appid):
        to_get.append(appid)

print len(to_get), "apps to process"


count = 0


for appid in to_get[:max_page]:
    apppath = os.path.join(imagepath, appid)
    filelist = os.listdir(apppath)
    for imagename in filelist:
        image = cv2.imread(os.path.join(apppath, imagename), cv2.IMREAD_COLOR)
        imgurl = imgToUrl[imagename]
        imageSet.add(imgurl, image)
    imageSet.addapp(appid)
    count += 1
    print "count", count
 


imageSet.dumpall()