# -*- coding:utf-8 -*-
import requests, json
import os, sys
import re, time
from Queue import Queue
import threading
from bs4 import BeautifulSoup



def searchBaidu(searchName, page_num):
    searchName = searchName+' 名字'.decode("utf-8")
    url = "https://www.baidu.com/s?"
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}  

    data = {'wd': searchName,
            'pn': str(page_num*10),
            }

    r = requests.get(url, params=data, headers=headers, timeout=5)

    return r.text.encode('utf-8') 



def add_pages_to_folder(searchName, content, filename, baidu_folder):   
    folder = os.path.join(baidu_folder)
    if not os.path.exists(folder):  
        os.mkdir(folder)
    filename = os.path.join(folder, filename)
    with open(filename, 'w') as f:
        f.write(searchName+"\n")
        f.write(content)               


def parse(response):
    soup = BeautifulSoup(response,"html5lib")
    headline = [re.sub(u'<[\d\D]*?>',' ',str(item)) for item in soup.select('div.result h3.t > a')]
    return "\n".join(headline)
    

def search(id_name_list, max_page):


    #to use multi-threading
    def working(to_search_queue):
        global count
        while not to_search_queue.empty() and count<max_page:
            appid, searchName = to_search_queue.get()
            print searchName
            contents = [''] * 5
            got = [False] * 5
            for page_num in range(5):
                try:
                    baiduContent = searchBaidu(searchName, page_num)
                    contents[page_num] = baiduContent 
                    got[page_num] = True
                except Exception, e:
                    print "Exception: ", e
                    exceptionlog.write('app:{} name: {} exception: {}\n'.format(appid, searchName, str(e)))
                    continue
            ### added
            content = ""
            for con in contents:
                content+="\n"+parse(con)

            for page_num in range(5):
                if got[page_num]:
                    add_pages_to_folder(searchName, content, str(appid)+'.txt', baidu_folder)

            count += 1
            print 'thread {} searched:{}, appid: {}'.format(threading.current_thread().getName(), searchName, appid)


    
    
    #count
    global count
    count = 0


    if not os.path.exists(baidu_folder):  
        os.mkdir(baidu_folder)

    baidulist = os.listdir(baidu_folder)
    
    #construct to-get-queue
    to_search_queue = Queue()
    for appid, searchName in id_name_list:
        if not appid in baidulist:
            to_search_queue.put((appid, searchName))
        elif len(os.listdir(os.path.join(baidu_folder, appid)+'/')) < page_per_app:
            to_search_queue.put((appid, searchName))

    print to_search_queue.qsize(), "names to search"

    exceptionlog = open('exception.log', 'a')
    exceptionlog.write('\n\n'+'-'*70+'\n'+time.asctime(time.localtime(time.time()))+'\n')

    NUM = 10
    threads = []
    for i in range(NUM):
        t = threading.Thread(target=working, name=str(i), args=(to_search_queue,))
        t.setDaemon(True)
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    #write exception.log's ending
    exceptionlog.write('\n'+'-'*70+'\n\n')
    exceptionlog.close()


baidu_folder = "baidu_result/"
page_per_app = 5

id_name_list = []
with open('app_name.txt', 'r') as f:
    for line in f.readlines()[:10]:
        line = line.strip().split('\t')
        id_name_list.append((line[0], line[1]))

search(id_name_list, 10)
