#!/usr/bin/env python
#encoding=utf-8
"""
增加你搜索的是不是？
方法使用局部靠近的hash，见（图片hash搜索）
"""
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene
import jieba
from java.io import File
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import NumericRangeQuery
from org.apache.lucene.util import Version
import string
import json

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""


class GameSearcher:
    def __init__(self,vm_env):
        self.STORE_DIR = "index"
        vm_env.attachCurrentThread()
        print 'lucene', lucene.VERSION
        self.directory = SimpleFSDirectory(File(self.STORE_DIR))
        self.searcher = IndexSearcher(DirectoryReader.open(self.directory))
        self.analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
        #在两种搜索方式时的各种field的权重
        self.weights = {
            "title":{
                "name":10,
                "names":5,
                "tags":3,
                "description":1,
                "review":0.8
            },
            "content":{
                "name":0,
                "names":0,
                "tags":0,
                "description":1,
                "review":0.8
            }
        }
    
    def namemodifier(self,name):
        #假设输入的是名字，把输入的query中的标点去掉
        punctuation = (string.punctuation+"‘（）。，、；’【、】`～！￥%……&×——+=-|：”《》？,™,の,®").decode('utf-8')
        tempname = ""
        name = name.decode("utf8")
        for i in range(len(name)):
            if name[i] not in punctuation:
                tempname+=name[i]
        return tempname.encode("utf8")

    def producersearch(self,command):
        #通过公司搜索
        command = " ".join(jieba.cut(command))
        query = QueryParser(Version.LUCENE_CURRENT, "producer",self.analyzer).parse(command)
        scoreDocs = self.searcher.search(query, 20).scoreDocs
        res = [self.searcher.doc(scoredoc.doc) for scoredoc in scoreDocs]
        return res


    def keywordsearch(self,command,rankmod=0,searchmod="title"):
        """
        rankmod 可以是可以改变的优先级排序，比如可以是“画质”，“剧情”，“人设”，“打击感”等等
        KeyWords = ["画面","剧情","人物","操作","音乐","创意"] 用1,2,3,4,5，6表示 0表示默认排序
        searchmod title和content 分别是通过标题，标签等等信息和通过描述评论等等信息搜索。
        返回一个doc字典构成的list
        方法：
            使用lucene搜索特定的域，把搜索的结果整合起来，把lucene返回的score按照不同的权重相加，
            name域的相加方法是一个非线性的函数
            再通过rankmod参数叠加一个sentiment analysis得到的score，最后得出排序结果
        """
        rank = {}
        info = {}
        #第一级 搜索名字
        if not self.namemodifier(command):
            return
        query = QueryParser(Version.LUCENE_CURRENT, "name",self.analyzer).parse(self.namemodifier(command))
        scoreDocs = self.searcher.search(query, 20).scoreDocs
        for scoreDoc in scoreDocs:
            #print scoreDoc.score,self.searcher.doc(scoreDoc.doc).get("name")
            docid = self.searcher.doc(scoreDoc.doc).get("id")
            rank[docid] = 2.8**(scoreDoc.score-1)
            info[docid] = self.searcher.doc(scoreDoc.doc)
        
        command = " ".join(jieba.cut(command))
        for field in self.weights[searchmod].keys():
            query = QueryParser(Version.LUCENE_CURRENT, field,self.analyzer).parse(command)
            scoreDocs = self.searcher.search(query, 20).scoreDocs
            for scoreDoc in scoreDocs:
                docid = self.searcher.doc(scoreDoc.doc).get("id")
                rank[docid] = rank.get(docid,0)+scoreDoc.score*self.weights[searchmod][field]
                info[docid] = self.searcher.doc(scoreDoc.doc)
        
        if rankmod:
            for i in rank.keys():
                vector = info[i].get("vector")
                if vector:
                    vector = vector[1:-1].split(",")
                    #print rank[i],vector[rankmod-1]
                    rank[i]+=float(vector[rankmod-1])*1000
        
        ran = sorted(rank.items(),key = lambda x :x[1],reverse=True)
        res = [info[i[0]] for i in ran] 
        return res
            # print doc.getField("id").numericValue()
            # print 'id:', doc.get("id"),'name:', doc.get("name"), '\ndescription:', doc.get("description"),'\nlist:', doc.get("list"),'\nseries:', doc.get("series"),'\nvector:', doc.get("vector"),"\n\n"
    
    def idget(self,ID):
        """
        用于前端获得网页信息，其中评论不是从lucene中取得，而是由从steam爬下来的源文件取得，这样包含评论用户名等信息
        """
        query = NumericRangeQuery.newIntRange("id", ID, ID, True, True)
        scoreDocs = self.searcher.search(query, 20).scoreDocs
        if not scoreDocs:
            return None
        res = {}
        doc = self.searcher.doc(scoreDocs[0].doc)
        res["id"] = doc.get("id")
        res["cover"]    =   doc.get("cover")
        res["name"] =   doc.get("name")
        res["names"]    =   doc.get("names")
        res["tags"] =   doc.get("tags")
        res["producer"] = doc.get("producer")
        res["price"]  =   doc.get("price")
        # print type(doc.get("urls"))
        try:
            res["related"]  =   doc.get("related").split()
        except:
            res["related"] = []
        vector = []
        if doc.get("vector"):
            for i in doc.get("vector")[1:-1].split(","):
                vector.append(float(i))
            assert len(vector) == 6
        res["vector"] = vector
        root  = os.path.join("../datastore/steam_reviews",str(ID))
        try:
            reviews = []
            for f in os.listdir(root):
                with open(os.path.join(root,f),"r") as ff:
                    content = json.load(ff)
                    for i in content.get("reviews",[]):         
                        reviews.append(i)
            #print reviews
            res["review"] = reviews #这样的review具有标点符号和用户信息
        except :
            pass
        root = os.path.join("../datastore/json_info/",str(ID)+".json")
        with open(root,"r") as ff:
            content = json.load(ff)
            res["description"]  = content.get("description")
            res["urls"] = content.get("urls")
        
        return res


vm_env=lucene.initVM(vmargs=['-Djava.awt.headless=true'])
searcher = GameSearcher(vm_env)
if __name__ == '__main__':
    
    # if False:
    if True:
        while True:
            for i in searcher.keywordsearch(raw_input(),0):#.decode("utf8")):
                print i.get("id"),i.get("name")#,i.get("vector")
                pass
    elif True:
        d = searcher.idget(437920)
        if d:
            print d.get("id"),d.get("name"),d.get("urls"),d.get("producer")
            print d.get("price"),d.get("description")
            print d.get("related")
            print d.get("vector")
            print d.get("names")
            print "reviews",len(d.get("review"))
            print type(d.get("name"))
            # print type(d.get("urls"))
            # print type(d.get("related"))
            # print type(d.get("vector"))
            # for a in d.get("review"):
            #     print a["review"]
        while True:
            d = searcher.idget(int(raw_input()))
            if d:
                print d.get("id"),d.get("name"),d.get("urls"),d.get("producer")
                print d.get("price"),d.get("description")
                print d.get("related")
                print d.get("vector")
                print d.get("names")
                print "reviews",len(d.get("review"))
                #print d.get("review")
                
    else:
        # ds = searcher.keywordsearch("Wolf Gang")
        ds = searcher.producersearch("arts")
        for d in ds:
            print d.get("id"),d.get("name")
        print searcher.idget(932843949).get('name')
    