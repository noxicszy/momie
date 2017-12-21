#-^-coding:utf-8-^-
import re
import math
import string
import pickle
"""
利用LSH方法，主要分为两个部分，第一个是存储所有的名字到bucket里面，第二个是利用bucket的初步hash功能，来寻找可能长得像的词条，
最后再计算嫌疑词条和query词条的edit distance. 得到最终的疑似词条。
为了避免多次加载，把数据存到datastore里面。！！！记得要手动更新名字集
"""

class QueryCorrecter():
    def __init__(self):
        self.keys = [[5, 8, 13, 22, 23, 28, 29, 33, 36, 39, 44, 49, 50],[1, 3, 4, 9, 15, 17, 21, 27, 40, 42, 43, 46, 48],
                    [7, 11, 12, 14, 16, 19, 20, 26, 37, 38, 41, 45, 51], [2, 6, 10, 18, 24, 25, 30, 31, 32, 34, 35, 47, 52],
                    [9, 12, 18, 19, 25, 30, 34, 41, 44, 45, 47, 49, 51],[6, 13, 15, 19, 20, 25, 36, 39, 44,48, 50, 51, 52]
        ]
        self.stordir = "../datastore/querycorrection.pkl"
        try:
            with open(self.stordir,"rb") as f:
                self.buckets = pickle.load(f)
        except:
            print "generating buckets"
            self.buckets = []
            self.storename()
        pass

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
        for i in range(len(self.keys)):
            self.buckets.append(["" for i in range(2**13)])
        for docnum in xrange(0, ireader.numDocs()):
            doc = ireader.document(docnum)
            name = doc.get("name")
            for i in range(len(self.keys)):
                pos = self.calvec(name,self.keys[i])
                self.buckets[i][pos] = self.buckets[i][pos]+name+'\t'
        with open(self.stordir,"wb") as f:
            pickle.dump(self.buckets,f)
        



    def hashvalue(self,p,c,d):
        # #p:d dimension integer vector list
        # #c:the wei
        # #d:取的位 从1开始
        res = []
        for dd in d:
            dd -=1
            i = dd/c
            if p[i]>dd%c:
                res.append(1)
            else: 
                res.append(0)
       
        return res

    def calvec(self,intext,d):
        """
        很难找到特征，目前解决方案：将整个单词长度分为2份，字母表按长度分为13份。统计个数，生成52维整数向量
        取其中的13维，这样平均一个bucket四个左右，再变成hamming数
        现在的问题 只有单词长度在26以上时，才有可能达到2的13次方
        已在后面加上了非线性变换
        num  =float(num)/2
        num = num**(0.5)*2**7
        """
        text = ""
        for i in intext:
            if i in string.ascii_letters or i in string.digits:
                text = text+i
        # text = re.sub(r'\d+',"",text)
        # text = re.sub(r'\s+',"",text)
        text = str(text.lower())
        vector = []
        a = len(text)/2
        for i in range(2):
            tempvec = [0]*13
            for j in range(a):
                tempvec[ord(text[i*a+j])%13]+=1 #TODO：此处是%还是/有待讨论
            vector +=tempvec
        #print len(vector)

        return self.hashvec2num(self.hashvalue(vector,2,d))

    def hashvec2num(self,vec):
        num = 0
        for i in vec:
            num = num*2+i
        #为了更加均匀
        num  =float(num)/2
        num = num**(0.5)*2**7
        return int(num)
                
correcter = QueryCorrecter()
#while True:
for text in ["tunryourdestiny","trunthofedstiny","tunoureestany","turnourdetiny"]:
    #text = raw_input()
    ans = ""
    print text
    for i in range(len(correcter.keys)):
        pos = correcter.calvec(text,correcter.keys[i])
        #print correcter.buckets[i][pos]
        res = correcter.buckets[i][pos]
        res = res.lower()
        res = re.sub(r'\s+',"",res)
        # text = text.lower()
        # text = re.sub(r'\s+',"",text)
        ans = ans+res
        #print res
    assert "turnyourdestiny" in ans
    #print ans
    


