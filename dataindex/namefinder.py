#-^-coding:utf-8-^-
"""
上百度搜索，找关键词
前几页如果有很多很多重复的内容，就多找几页
搞到了大量的百度搜索结果，自己内部先统计一下rf-idf，删去没用的大量的重复词汇，之后再用百度验证
"""
import urllib2
import urllib
from bs4 import BeautifulSoup
import sys
import re

"""
with open('data.txt','wa') as f:
    key_word = []
    with open('key_word.txt','r') as kf:
        for line in kf:
            request = urllib2.Request('http://www.baidu.com/s?wd='+urllib.quote(line.strip().decode(sys.stdin.encoding).encode('utf8')))
            response = urllib2.urlopen(request)

            soup = BeautifulSoup(response.read())
            print soup.select('div.result h3.t > a')
            data = [re.sub(u'<[\d\D]*?>',' ',str(item)) for item in soup.select('div.result h3.t > a')]

            for item in data:
                f.writelines(''.join(item.strip().split())+'\n')
"""
class namefinder:
    def __init__(self):
        self.auxiliary_keys = ["叫什么","原名","又名"]

    def count_appear(self,strings,target):
        count = 0
        #print "[count_target]",target
        for line in strings:
            #print line.decode("utf8")
            for word in target.split():
                if word in line:
                    count +=1
        print '【###】',count
        return count/len(target.split())
    def search_name(self,name,auxiliary):
        """
        return a list contains the probably name 
        """
        pn = 0
        data = []
        while True:
            request = urllib2.Request('http://www.baidu.com/s?wd='+urllib.quote(name+" "+auxiliary.decode(sys.stdin.encoding).encode('utf8')+"&pn=%d"%pn))
            response = urllib2.urlopen(request)
            soup = BeautifulSoup(response.read(),"html5lib")
            newdata = [re.sub(u'<[\d\D]*?>',' ',str(item)) for item in soup.select('div.result h3.t > a')]
            print newdata
            if not len(newdata):
                break
            if (self.count_appear(newdata,name)+0.0)/len(newdata) < 0.5:
                break
            pn += 10
            for line in newdata:
                newname = line
                for word in name.split():
                    newname = newname.replace(word," ")
                data.append(re.sub(u'\s',' ',newname).decode("utf-8"))
        return data
        

    
    def check_name(self,alias,name):
        pass
if __name__=="__main__":
    finder = namefinder()
    for line in finder.search_name("tricky tower",finder.auxiliary_keys[0]):
        print line.encode("utf8").decode("utf-8")
