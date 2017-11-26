
import requests, json
import os, sys
import re, time
from Queue import Queue
import threading

def genNameToUrl(indexFileName):
    nameToUrl = {}
    indexFile = open(indexFileName)
    
    for line in indexFile.readlines():
        line = line.strip().split('\t')
        url, name = line[0], line[1]
        nameToUrl[name] = url
    indexFile.close()
    return nameToUrl

def getReview(appid, page_num):
    appid = str(appid)
    url = "http://store.steampowered.com/appreviews/"+appid+"?json=1"
    data = {'filter': 'all',
                        'language': 'zh-CN',
                        'day_range': '10000',
                        'start_offset': str(page_num*20),
                        'review_type': 'all',
                        'purchase_type': 'all'}

    header = {
        "Accept-Language" : "zh-CN,zh", 
    }
    r = requests.get(url, params=data,  headers=header, timeout=60)
    return r.text.encode('utf-8')

def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))



def add_review_to_folder(appid, review, filename):   
    folder = "./steam_reviews/"+appid
    if not os.path.exists(folder):  
        os.mkdir(folder)
    filename = os.path.join(folder, filename)
    f = open(filename, 'w')
    f.write(review)               
    f.close()

def fetchReviews(htmlpath):

    nameToUrl = genNameToUrl('index.txt')
    filelist =  os.listdir(htmlpath)
    review_folder = "steam_reviews"

    if not os.path.exists(review_folder):  
        os.mkdir(review_folder)

    appid_queue = Queue()
    for filename in filelist:
        store_url = nameToUrl[filename]
        appid = getID(store_url)
        appid_queue.put(appid)

    global count
    count = 0
    exceptionlog = open('exception.log', 'a')
    exceptionlog.write(time.asctime(time.localtime(time.time()))+'\n')
    def working(appid_queue):
        global count
        while not appid_queue.empty():
            appid = appid_queue.get()
            for page_num in range(5):
                try:
                    review = getReview(appid, page_num) 
                except Exception, e:
                    print "Exception: ", e
                    exceptionlog.write(appid+": exception: "+str(e)+'\n')
                    continue
                add_review_to_folder(appid, review, str(page_num))
            count += 1
            print "thread", int(threading.current_thread().getName()), "fetched", appid, "count", count

    NUM = 10
    threads = []
    for i in range(NUM):
        t = threading.Thread(target=working, name=str(i), args=(appid_queue,))
        t.setDaemon(True)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    exceptionlog.close()
if __name__ == '__main__':

    htmlpath = str(sys.argv[1])
    fetchReviews(htmlpath)

