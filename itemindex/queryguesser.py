#-^-coding:utf-8-^-
import re
import math
import string
import pickle
from pypinyin import pinyin, lazy_pinyin
# from bisect import bisect_left,bisect_right 垃圾玩意不能自定义cmp函数
"""
用于客户端的实时尝试补全query。
特点：
    中文按照拼音匹配！！！
    英文对于最后一个单词有一定的容错率
调用：
    使用QueryGuesser()生成类
    调用时使用 qg.guess(query) 返回一个list，全部是可能的guess 注意query一定是utf8格式 list长度没有限制

原理：
    存储一个列表作为所有可行的猜测结果，使用二分搜索来寻找可能的结果
TODO:guess 的结果应该有个排序
"""

class QueryGuesser():
    def __init__(self):
        self.stordir = "../datastore/queryguesser.pkl"
        try:
            with open(self.stordir,"rb") as f:
                self.possibits = pickle.load(f) #所有可能的猜测的query
        except:
            print "generating buckets"
            self.possibits = []
            self.storename()
        
        self.last_query = ""
        self.last_l = 0
        self.last_h = len(self.possibits) #二分还要比划比划


    def storename(self):
        import lucene
        from java.io import File
        from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
        from org.apache.lucene.analysis.standard import StandardAnalyzer
        from org.apache.lucene.document import Document, Field, FieldType
        from org.apache.lucene.util import BytesRef, BytesRefIterator, Version
        from org.apache.lucene.analysis.core import WhitespaceAnalyzer
        from org.apache.lucene.index import Term
        from org.apache.lucene.store import SimpleFSDirectory
        from org.apache.lucene.index import \
        IndexWriterConfig, IndexWriter, DirectoryReader
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        STORE_DIR = "index"
        directory = SimpleFSDirectory(File(STORE_DIR))
        ireader = DirectoryReader.open(directory)
        for docnum in xrange(0, ireader.numDocs()):
            doc = ireader.document(docnum)
            names = doc.get("name")
            for name in names.split("\t"):
                self.possibits.append(self.modify(name))
        self.possibits.sort(cmp=self.comp)
        print self.possibits
        with open(self.stordir,"wb") as f:
            pickle.dump(self.possibits,f)
        
    
    def comp(self,a,b):
        for i in range(min(len(a),len(b))):
            aa = lazy_pinyin(a[i])[0]
            bb = lazy_pinyin(b[i])[0]
            if aa!=a[i]:
                aa = aa[0].upper() + aa[1:]
            else:
                aa = aa.lower()
            if bb!=b[i]:
                bb = bb[0].upper() + bb[1:]
            else:
                bb = bb.lower()
            if aa!=bb:
                return cmp(aa,bb)
        return cmp(len(a),len(b))

    def modify(self,intext):
        """
        输入字符串，各种语言皆可
        去掉所有符号
        简单分词 英文一词一分，其他语言一字一分
        返回一个由字符串组成的list
        """
        punctuation = (string.punctuation+"‘（）。，、；’【、】`～！￥%……&×——+=-|：”《》？,™,の,®").decode('utf-8')
        for i in range(len(intext)):
            if intext[i] in punctuation:
                intext = intext[:i] + ' ' + intext[i+1:]
        intext = re.sub(r'\s+'," ",intext)
        #intext = intext.lower()
        texts = []
        i,j = 0,0
        while j<len(intext):
            if (intext[j] in string.ascii_letters and intext[i] in string.ascii_letters) or (intext[j] in string.digits and intext[i] in string.digits):
                j+=1
            else:
                if i==j:
                    if intext[i]!=" ":
                        texts.append(intext[i])
                    j+=1
                    i+=1
                else:
                    texts.append(intext[i:j])
                    i = j
                    j = j
        if i != j:
            texts.append(intext[i:j])
        return texts


    def editsimilar(self,text1,text2):
        """
        不太一样的editdistance 只会匹配text1和text2的前（text1）的字母
        若text1和text2的首字母为英文小写，使用编辑距离容错匹配，直接返回是否相等
        """
        if len(text2)<len(text1)-2:
            return False
        if not(text1[0] in string.lowercase and text2[0]in string.lowercase):
            return not self.comp(text1,text2)
        l = min(len(text1),len(text2))+1
        distances = [[0]*(l) for i in range((l))]
        for i in range(l):
            distances[0][i] = i
        for j in range(l):
            distances[j][0] = j
        for i in range(l-1):
            for j in range(l-1):
                if text1[i]!=text2[j]:
                    distances[j+1][i+1] = min(distances[j][i],distances[j+1][i],distances[j][i+1])+1
                else: 
                    distances[j+1][i+1] = min(distances[j][i],distances[j+1][i],distances[j][i+1])
    
        return distances[-1][-1]<=min(2,len(text1)/4)
    
    def similar(self,a,b):
        if len(b)<len(a):
            return False
        if self.comp(a[:-1],b[:len(a)-1]):
            return False

        return self.editsimilar(a[-1].lower(),b[len(a)-1].lower())

    def bisect(self,x,comp=None):
        """
        self.possibits: the list
        x: the query
        cmp: compare function
        """
        low = self.last_l
        high = self.last_h-1
        if comp == None:
            comp = cmp
        mid = 0
        while(low <= high):  
            mid = (low + high)/2  
            midval = self.possibits[mid]  
            if comp(midval,x)==-1:  
                low = mid + 1   
            elif comp(midval , x)==1:  
                high = mid - 1   
            else:  
                break 
        if not self.similar(x,self.possibits[mid]):
            mid+=1
        #print "[]"+" ".join(self.possibits[mid]).encode("utf8")
        high = mid
        low = mid
        # for i in range(-10,10):
        #     print " ".join(self.possibits[mid+i])
        #模糊扩大范围
        while(high < len(self.possibits) and self.similar(x,self.possibits[high])):
            high+=1
        while(low>0 and self.similar(x,self.possibits[low-1])):
            low-=1
        self.last_h = high
        self.last_l = low
        ans = []
        i = 0
        while i<max(high-mid,mid-low):
            if i<high-mid:
                ans.append(self.possibits[mid+i])
            if i<mid-low and i:
                ans.append(self.possibits[mid-i])
            i+=1
        return ans

        




    def guess(self,query):
        """
        input the string query
        output with a list of guests
        """
        query = self.modify(query)
        #print query
        if query!=self.last_query[:len(query)]:
            self.last_h = len(self.possibits)
            self.last_l = 0
        res = []
        for i in self.bisect(query,self.comp):
            temp = ""
            for j in i:
                if j[0] in string.ascii_letters or j[0] in string.digits:
                    temp += " " +j+" "
                else:
                    temp += j
            temp = re.sub(r'\s+'," ",temp)
            res.append(temp.encode("utf8"))
        return res

    #print ans
if __name__=="__main__":
    qg = QueryGuesser()
    #print correcter.correct("aur kingdm")    
    # print qg.modify("abc12#4沃日#ri".decode("utf8"))
    while True:

        for i in qg.guess(raw_input().decode("utf8")):
            print "[res]",i


# for i in range(10):
#     print "逮".join(qg.possibits[i+80] ).encode("utf8")#前84至100多大概为中文
# for i in qg.guess("train simulator")


