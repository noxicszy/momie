# coding=utf-8
import re
import os
import json
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')
f = open('index.txt','r')
for line in f.xreadlines():		#逐行读取文本
    filename = line.strip().split('\t')[1]
    url = line.strip().split('\t')[0]
    rootdir = 'html'
    path = os.path.join(rootdir,filename)
    if os.path.isfile(path):
        tag_list=[]
        id_list = re.findall(r"app/(\d*)", url)
        appid = id_list[0]
        a = open(path).read()
        soup=BeautifulSoup(a,"html.parser")
        appname = soup.find("div",{'class':'apphub_AppName'}).get_text()
        
        appdes = soup.find("div",{'class':'game_description_snippet'}).get_text()
        try:
            appprice = soup.find("div",{'class':'discount_original_price'}).get_text()
        except:
            try:
                appprice = soup.find("div",{'class':'game_purchase_price price'}).get_text()
            except:
                appprice = soup.find("div",{'class':'discount_final_price'}).get_text()
        basic_picture = soup.find("img",{'class':'game_header_image_full'}).attrs['src']

        sysreq = soup.find("div",{'class':'game_page_autocollapse sys_req'}).get_text()

        patern = re.compile('<img src="(.+116x65.+)">'.decode('utf-8'))
        image_urls = patern.findall(soup)
        
        apptags = soup.findAll("a",{'class':'app_tag'})
        for i in range(0,len(apptags)):
            tag_list.append(apptags[i].get_text().strip())

        if(soup.find("div",{'id':'developers_list'})):
            appdevelop = soup.find("div",{'id':'developers_list'}).get_text().strip()
        else:
            appdevelop = ''

        review_root = os.path.join("steam_reviews",appid)
        if(os.path.exists(review_root)):
                list2 = os.listdir(review_root) #列出文件夹下所有的目录与文件
                rstr = ''
                flag = []
                for j in range(0,len(list2)):
                    path2 = os.path.join(review_root,list2[j])
                    if os.path.isfile(path2):
                        b = open(path2)
                        js = json.load(b)
                        review_list = js[u"reviews"]
                        for rev in review_list:
                            if rev[u'review'] not in flag:
                                rstr = rstr+'\n'+rev[u'review']
                                flag.append(rev[u'review'])
                            else:
                                continue
                            
                        
        else:
                rstr = ''
        respath = "basic_info/"+ appid
        res = open(respath,'wb')
        res.write("appid: ")
        res.write(appid.encode('utf-8'))
        res.write('\n')
        res.write("appname: ")
        res.write(appname.encode('utf-8'))
        res.write('\n')
        res.write("apptags: ")
        count = 0
        for item in tag_list:
            if count < 5:
                res.write(item.encode('utf-8'))
                res.write('\t')
            else:
                break
        res.write('\n')
        res.write("appdevelopers: ")
        res.write(appdevelop.encode('utf-8'))
        res.write('\n')
        res.write("reviews: ")
        res.write(rstr.encode('utf-8'))
        res.close()
        print sysreq

