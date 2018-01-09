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
            names = doc.get("name")
            for name in names.split("\t"):
                for i in range(len(self.keys)):
                    pos = self.calvec(name,self.keys[i])
                    self.buckets[i][pos] = self.buckets[i][pos]+name+'\t'
        with open(self.stordir,"wb") as f:
            pickle.dump(self.buckets,f)
        

    def modify(self,intext):
        text = ""
        for i in intext:
            if i in string.ascii_letters or i in string.digits:
                text = text+i
        text = str(text.lower())
        return text
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
        text = self.modify(intext)
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

    def editdistancce(self,text1,text2):
        # text1 = text1
        # text2 = text2
        distances = [[0]*(len(text1)+1) for i in range((len(text2)+1))]
        for i in range(len(text1)+1):
            distances[0][i] = i
        for j in range(len(text2)+1):
            distances[j][0] = j
        for i in range(len(text1)):
            for j in range(len(text2)):
                if text1[i]!=text2[j]:
                    distances[j+1][i+1] = min(distances[j][i],distances[j+1][i],distances[j][i+1])+1
                else: 
                    distances[j+1][i+1] = min(distances[j][i],distances[j+1][i],distances[j][i+1])
        return distances[-1][-1]

    def correct(self,name):
        ans = {}
        for i in range(len(correcter.keys)):
            pos = correcter.calvec(name,correcter.keys[i])
            res = correcter.buckets[i][pos]
            res = res.split("\t")
            for r in res: 
                r = self.modify(r)
                ans[r] = ans.get(r,0)+1
        corre = sorted(ans.items(),key = lambda x: x[1],reverse=True)
        name = self.modify(name)
        for r in corre:
            if self.editdistancce(name,r[0]) < float(len(name))/3.5:
                return r[0]

    #print ans
correcter = QueryCorrecter()
if __name__ == '__main__':
    print correcter.correct("aurckingdm")


