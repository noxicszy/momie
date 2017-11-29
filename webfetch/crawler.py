# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from BloomFilter import BloomFilter
from Queue import Queue
import urllib2, urlparse, urllib, cookielib, requests
import os, sys, time, re
import threading
import pickle


def load_pickle(seed, max_page):
    #read crawled 
    if not os.path.exists('crawled.pkl'):
        crawled = []
    else:
        crawled_pklf = open('crawled.pkl', 'rb')
        crawled = pickle.load(crawled_pklf)
        crawled_pklf.close()

    
    #read bloomfilter
    if not os.path.exists('bloomFilter.pkl'):
        bloomFilter = BloomFilter(max_page)
    else:
        bloomFilter_pklf = open('bloomFilter.pkl', 'rb')
        bloomFilter = pickle.load(bloomFilter_pklf)
        bloomFilter_pklf.close()

    #read to-crawl queue
    
    if not os.path.exists('tocrawl.pkl'):
        tocrawl_list = [seed]
    else:
        tocrawl_pklf = open('tocrawl.pkl', 'rb')
        tocrawl_list = pickle.load(tocrawl_pklf)
        tocrawl_pklf.close()
        tocrawl_list = [seed] + tocrawl_list

    tocrawl = Queue()
    for page in tocrawl_list:
        tocrawl.put(page)
        
    return crawled, bloomFilter, tocrawl, tocrawl_list


def dump_pickle(crawled, bloomFilter, tocrawl_list):
    
    def dumpit(data, filename):
        pickle_file = open(filename, 'wb')
        pickle.dump(data, pickle_file)
        pickle_file.close()

    dumpit(crawled, 'crawled.pkl')
    dumpit(bloomFilter, 'bloomFilter.pkl')
    # dump tocrawl_list in fact
    dumpit(tocrawl_list, 'tocrawl.pkl')



def isapp(url):
    return ("http://store.steampowered.com/app/" in url)


def getID(store_url):
    m = re.search("app/(\d+)/*", store_url)
    return str(m.group(1))



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



def crawl(page_number, htmlpath):
    global tocrawl, crawled, graph, count, crawling, bloomFilter,varLock
    
    varLock = threading.Lock()
    graph = {}
    count = 0
    NUM = 10


    def working(page_number, htmlpath):
        global count
        while True:
            page = tocrawl.get()
            tocrawl_list.pop()
            if not bloomFilter.query(page):
                bloomFilter.add(page)
                # skip apps with crawled ID, even though their url may change a litlle 
                if isapp(page):
                    if bloomFilter.query(getID(page)):
                        print page, " is in bloomFilter"
                        continue
                    else:
                        bloomFilter.add(getID(page))

                

                print "thread", int(threading.current_thread().getName()), "is crawling", page
                
                try:
                    content = get_page(page)
                except Exception, e:
                    print e
                    continue
                
                #save app pages
                if isapp(page):
                    if varLock.acquire():
                        if count >= int(page_number):
                            varLock.release()
                            break
                        else:
                            add_page_to_folder(page, content, htmlpath)
                            crawled.append(page)
                            count += 1

                            #pickle dump
                            dump_pickle(crawled, bloomFilter, tocrawl_list)

                        varLock.release()

                    print "thread", int(threading.current_thread().getName()), "crawlerd", page, "pagecount", count
                
                outlinks = get_all_links(content, page)
                graph[page] = outlinks

                for link in outlinks:
                    if len(link) < 220 and ('http://store.steampowered.com/app/' in link or 'http://store.steampowered.com/games/' in link or 'http://store.steampowered.com/tag/' in link):
                        tocrawl.put(link)
                        tocrawl_list.append(link)
            else:
                print page, " is in bloomFilter"
            
    threads = []
    for i in range(NUM):
        t = threading.Thread(target=working, name=str(i), args=(page_number, htmlpath))
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

    htmlpath = "html/"
    seed = "http://store.steampowered.com/games/"
    #number of pages to crawled in one round
    page_number = 100

    #number of all steam apps
    MAX_PAGE = 100000
    #set cookie
    cookie = {
            'birthtime' : '28801',
            'path' : '/',
            'domain' : 'store.steampowered.com',
            'mature_content' : '1',

            }

    #load data
    crawled, bloomFilter, tocrawl, tocrawl_list = load_pickle(seed, MAX_PAGE)

    start_time = time.time()

    graph, crawled = crawl(page_number, htmlpath)
    dump_pickle(crawled, bloomFilter, tocrawl_list)

    delta_time = time.time() - start_time
    print str(delta_time) + 's'
    print len(crawled),'pages crawled' 