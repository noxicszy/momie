# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from BloomFilter import BloomFilter
from Queue import Queue
import urllib2, urlparse, urllib, cookielib
import re
import os, sys
import threading
import time
import requests

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):


    # req=urllib2.Request(page)
    # req.add_header('mature_content', '1')
    # req.add_header('path', '/')
    # response = urllib2.urlopen(req, timeout = 10)

    response = requests.get(page, cookies=cookie)
    content = response.text.encode('utf-8')
    return content

def get_all_links(content, page):
    links = []
    soup = BeautifulSoup(content, "html.parser")
    for url in soup.findAll('a',{'href': re.compile('^http|^/')}):
            links.append(str(urlparse.urljoin(page, url.get('href')).encode('utf-8')))
    return links
        
def union_dfs(a,b):
    for e in b:
        if e not in a:
            a.append(e)
            
def union_bfs(a,b):
    for e in b:
        if e not in a:
            a[0:0] = [e]
       
def add_page_to_folder(page, content): 
    index_filename = 'index.txt'    
    folder = 'html'                 
    filename = valid_filename(page) 
    index = open(index_filename, 'a')
    index.write(page.decode('utf-8').encode('ascii', 'ignore') + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(content)               
    f.close()



def crawl(seed, max_page):
    global tocrawl, crawled, graph, count, crawling, bloomFilter,varLock
    bloomFilter = BloomFilter(max_page)
    varLock = threading.Lock()
    tocrawl = Queue()
    tocrawl.put(seed)
    crawled = []
    graph = {}
    count = 0
    NUM = 10
    crawling = [''] * NUM


    def working(max_page):
        global count
        while True:
            page = tocrawl.get()

            # if (page not in crawling) and (not bloomFilter.query(page)):
            if not bloomFilter.query(page):
                bloomFilter.add(page)
                
                print "thread", int(threading.current_thread().getName()), "is crawling", page
                
                try:
                    content = get_page(page)
                except Exception, e:
                    print e
                    continue

                if varLock.acquire():
                    if count >= int(max_page):
                        varLock.release()
                        break
                    else:
                        crawled.append(page)
                        # bloomFilter.add(page)
                    varLock.release()
                
                if "http://store.steampowered.com/app/" in page:
                    add_page_to_folder(page, content)
                    count += 1
                    print "thread", int(threading.current_thread().getName()), "crawlerd", page, "pagecount", count
                
                outlinks = get_all_links(content, page)
                graph[page] = outlinks

                for link in outlinks:
                    if len(link) < 220 and ('http://store.steampowered.com/app/' in link or 'http://store.steampowered.com/games/' in link or 'http://store.steampowered.com/tag/' in link):
                        tocrawl.put(link)
  
                # crawling[int(threading.current_thread().getName())] = ''
            
    threads = []
    for i in range(NUM):
        t = threading.Thread(target=working, name=str(i), args=(max_page,))
        t.setDaemon(True)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return graph, crawled



if __name__ == '__main__':
    # seed = sys.argv[1]
    # max_page = sys.argv[2]
    # max_page = int(max_page)

    seed = "http://store.steampowered.com/games/"
    max_page = 1000

    cookie = {
            'birthtime' : '28801',
            'path' : '/',
            'domain' : 'store.steampowered.com',
            'mature_content' : '1',

            }

    start_time = time.time()
    graph, crawled = crawl(seed, max_page)
    delta_time = time.time() - start_time
    print str(delta_time) + 's'
    print len(crawled),'pages crawled' 