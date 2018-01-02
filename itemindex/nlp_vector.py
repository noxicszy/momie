#-^-coding:utf-8-^-
"""
本程序用来生成每一个game的vector
game的vector由如下构成
1,2,3,4,5这五个数字代表游戏在 画面,剧情,人物,操作,创意 的得分
"""
from gensim.models import Word2Vec
import sys, os, lucene, threading, time
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import SimpleAnalyzer,WhitespaceAnalyzer
import json
import pickle


from gameindexer import IndexFiles

# lucene.initVM(vmargs=['-Djava.awt.headless=true'])
# analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
# indexer = IndexFiles( "index", analyzer)

mod = Word2Vec.load(r'../datastore/nlp_vector/Word60.model')
KeyWords = ["画面","剧情","人物","操作","音乐","创意"]
#load sentimentscore
sentimentdic = {}
with open("sentiment_score.txt","r") as f:
    for line in f.readlines():
        line = line.strip()
        if line:
            sentimentdic[line.split()[0]] = float(line.split()[1])

#print sentimentdic["好"]

root = "../datastore/duple_words"
count = 0
data = {}
datadir = "../datastore/vector_info"
for root, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if not filename.endswith('.json') and not filename.endswith('.JSON'):
            continue
        path = os.path.join(root, filename)
        contents = None
        with open(path,"r") as fil:
            contents = json.load(fil)
        if not contents:
            continue
        vector = [0]*len(KeyWords)
        cont = 0.001
        for k in contents.values():
            for tup in k:
                cont+=1
                for i in range(len(KeyWords)):
                    if tup[0] in mod.index2word:
                        vector[i]+=mod.similarity(tup[0],KeyWords[i].decode("utf8"))*sentimentdic.get(tup[1].encode("utf8"),0)
                        # print mod.similarity(tup[0],KeyWords[i].decode("utf8")),sentimentdic.get(tup[1].encode("utf8"),0)
        vector = [2*i/cont for i in vector]
        count+=1
        data[int(filename.split(".")[0])] = vector
        print filename.split(".")[0],count #这个速度3万个大概要跑两天（不过可以分到不同文件夹里面去跑）
        if count%200 == 0:
            with open(os.path.join(datadir,"{}.pkl".format(count/200)),"wb") as f:
                pickle.dump(data,f)
                data = {}
with open(os.path.join(datadir,"{}.pkl".format(count/200)),"wb") as f:
    pickle.dump(data,f)





            
            





