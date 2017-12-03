# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from BloomFilter import BloomFilter
from Queue import Queue
import urllib2, urlparse, urllib, cookielib, requests
import os, sys, time, re
import threading
import pickle

def dumpall(bloomFilter, tocrawl_list):
    
    def dump_pickle(data, filename):
        pickle_file = open(filename, 'wb')
        pickle.dump(data, pickle_file)
        pickle_file.close()

    dump_pickle(bloomFilter, 'bloomFilter.pkl')
    # dump tocrawl_list in fact
    dump_pickle(tocrawl_list, 'tocrawl.pkl')



def isapp(url):
    return ("http://store.steampowered.com/app/" in url)


def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))

def isInSteam(page):
    return  'http://store.steampowered.com/app/' in page or \
            'http://store.steampowered.com/games/' in page or \
            'http://store.steampowered.com/software/' in page or \
            'http://store.steampowered.com/tag/' in page or \
            'http://store.steampowered.com/search/' in page 


def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):
    response = requests.get(page, cookies=cookie, timeout=30)
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
       
def add_page_to_folder(page, content, htmlpath): 
    filename = valid_filename(page)
    index_filename = 'index.txt'
    if not os.path.exists(index_filename):
        index = open(index_filename, 'w')             
    else:
        index = open(index_filename, 'a')
    index.write(page.decode('utf-8').encode('ascii', 'ignore') + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(htmlpath):  
        os.mkdir(htmlpath)
    f = open(os.path.join(htmlpath, filename), 'w')
    f.write(content)               
    f.close()


def genNameToUrl(indexFileName):
    nameToUrl = {}
    indexFile = open(indexFileName)
    
    for line in indexFile.readlines():
        line = line.strip().split('\t')
        url, name = line[0], line[1]
        nameToUrl[name] = url
    indexFile.close()
    return nameToUrl

def preload(seed, max_page):

    # load bloomfilter
    if not os.path.exists('bloomFilter.pkl'):
        bloomFilter = BloomFilter(max_page)
    else:
        bloomFilter_pklf = open('bloomFilter.pkl', 'rb')
        bloomFilter = pickle.load(bloomFilter_pklf)
        bloomFilter_pklf.close()


    # load to-crawl queue and list
    if not os.path.exists('tocrawl.pkl'):
        tocrawl_list = [seed]
    else:
        tocrawl_pklf = open('tocrawl.pkl', 'rb')
        tocrawl_list = pickle.load(tocrawl_pklf)
        tocrawl_pklf.close()
        if seed:
            tocrawl_list = [seed] + tocrawl_list

    tocrawl = Queue()
    for page in tocrawl_list:
        tocrawl.put(page)


    # get crawled app
    nameToUrl = genNameToUrl('index.txt')
    htmllist =  os.listdir(htmlpath)
    crawled_app = [False] * 10000000

    for filename in htmllist:
        url = nameToUrl[filename]
        appid = int(getID(url))
        crawled_app[appid] = True

    return bloomFilter, crawled_app, tocrawl, tocrawl_list





def crawl(page_number, htmlpath):
    global tocrawl, tocrawl_list, count, bloomFilter, crawled_app, varLock
    




    varLock = threading.Lock()
    graph = {}
    count = 0
    NUM = 20


    def working(page_number, htmlpath):
        global count
        while True:
            page = tocrawl.get()
            tocrawl_list.pop(0)
            if not bloomFilter.query(page):
                bloomFilter.add(page)

                # skip apps with crawled ID, even though their url may change a litlle 
                if isapp(page):
                    if crawled_app[int(getID(page))]:
                        # print "appid: {} has been crawled.".format(getID(page))
                        continue
                    else:
                        if varLock.acquire():
                            crawled_app[int(getID(page))] = True
                            varLock.release()

                # start fetching
                print "thread", int(threading.current_thread().getName()), "is crawling", page
                try:
                    content = get_page(page)
                except Exception, e:
                    print e
                    continue
                
                #save app pages
                if isapp(page):
                    if count >= int(page_number):
                        break
                    else:
                        add_page_to_folder(page, content, htmlpath)
                        count += 1
                        
                        #pickle dump
                        if count % 100 == 0:
                            dumpall(bloomFilter, tocrawl_list)

                        print "thread", int(threading.current_thread().getName()), "crawled", page, "appcount", count
                
                
                outlinks = get_all_links(content, page)

                for link in outlinks:
                    if len(link) < 220 and isInSteam(link) and not bloomFilter.query(link):
                        tocrawl.put(link)
                        tocrawl_list.append(link)

                # crawling for current page finished, add to bloomfilter
                

    threads = []
    for i in range(NUM):
        t = threading.Thread(target=working, name=str(i), args=(page_number, htmlpath))
        t.setDaemon(True)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return None



if __name__ == '__main__':

    MAX_PAGE = 200000 # number of all steam apps
    # seed = "http://store.steampowered.com/games/"
    htmlpath = sys.argv[1]
    page_number = int(sys.argv[2]) #number of pages to crawled in one round

    if len(sys.argv) < 4:
        seed = None
    else:
        seed = sys.argv[3]

    #set cookie
    cookie = {
            'birthtime' : '28801',
            'path' : '/',
            'domain' : 'store.steampowered.com',
            'mature_content' : '1',
            }

    #preload data
    bloomFilter, crawled_app, tocrawl, tocrawl_list = preload(seed, MAX_PAGE)

    start_time = time.time()

    crawl(page_number, htmlpath)
    dumpall(bloomFilter, tocrawl_list)

    delta_time = time.time() - start_time
    print str(delta_time) + 's'
    print sum(crawled_app),'pages crawled' 