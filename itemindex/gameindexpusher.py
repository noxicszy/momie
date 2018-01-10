#-^-coding:utf-8-^-
from gameindexer import IndexFiles
import gameindexer
import os
import pickle
import jieba
import json
gameindexer.lucene.initVM(vmargs=['-Djava.awt.headless=true'])
print 'lucene', gameindexer.lucene.VERSION
analyzer = gameindexer.SimpleAnalyzer(gameindexer.Version.LUCENE_CURRENT)
#--------------------------------------#
indexer = IndexFiles( "index", analyzer)
#--------------------------------------#
config = gameindexer.IndexWriterConfig(gameindexer.Version.LUCENE_CURRENT, analyzer)
config.setOpenMode(gameindexer.IndexWriterConfig.OpenMode.APPEND)
writer = gameindexer.IndexWriter(indexer.store, config)
searcher = gameindexer.IndexSearcher(gameindexer.DirectoryReader.open(indexer.store))

count = 0
def changes_nlpvector():
    global count
    root = "../datastore/vector_info"
    for root, dirnames, filenames in os.walk(root):
        for filename in filenames:
            print filename
            path = os.path.join(root, filename)
            contents = []
            with open(path,"rb") as f:
                try:
                    contents = pickle.load(f)
                except:
                    print "error"
            for i in contents:
                count+=1
                yield (i[0],[("vector",str(i[1]))])


def changes_similargames():
    root = "../datastore/related_games"
    for fil in os.listdir(root):
        with open(os.path.join(root,fil),"r") as f:
            try:
                appid = int(f.readline().split()[1])
                f.readline()
                related = " ".join(f.readline().split()[3:])
                yield (appid,[("related",related)])
            except Exception, e:
                print (fil,e)

def changes_name():
    with open("../datastore/id2ZHname.pkl" ,"rb") as f:
         content = pickle.load(f)
    # print content["321980"]
    for i in content.items():
        print i[0],i[1]
        print " ".join(jieba.cut(i[1]))
        yield int(i[0]),[("name",i[1].decode("utf8")),("names"," ".join(jieba.cut(i[1])))] 

def changes_guessednames():
    with open("../datastore/filtedguess.pkl" ,"rb") as f:
         content = pickle.load(f)
    for i in content:
        print " ".join(jieba.cut(i[1]))
        yield i[0],[("names"," ".join(jieba.cut(i[1])))] 

def change_orinames():
    root = "../datastore/json_info"
    for i in os.listdir(root):
        path = os.path.join(root,i)
        with open(path,"r") as f:
            content = json.load(f)
            yield int(i.split(".")[0]),[("name",content["name"])]

def changes_steamreviews():
    root = "../datastore/steam_reviews"
    for i in os.listdir(root):
        path = os.path.join(root,i)
        review = ""
        for fil in os.listdir(path):
            with open(os.path.join(path,fil),"r") as f:
                content = json.load(f)
                for a in content.get("reviews",[]):         
                    # f.write((i["review"]+".\n").encode("utf8"))
                    try:
                        review+=" ".join(jieba.cut(a["review"]))+" "
                    except Exception,e:
                        print e
        # print review
        yield int(i),[("review",review)]

     
# import mathplotlib
# import numpy as np  
# import matplotlib.pyplot as plt  
    

# x = []
# plt.grid(True)  
#     x.append(float(chan[1][0][1][1:-1].split(",")[0]))
# n,bins,patches=plt.hist(x,50,normed=1,facecolor='g',alpha=0.75)  
# plt.show()
# plt.xlabel('Smarts')  
# plt.ylabel('Probability')  
# plt.title('Histogram of IQ')  
# plt.text(60,.025, r'$\mu=100,\ \sigma=15$')  
# plt.axis([40,160,0,0.03])  
    
    
# for chan in changes_nlpvector():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)

# for chan in changes_similargames():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
#     #print chan[0],chan[1]
# #count  = 0
# writer.commit()
# for chan in changes_name():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
# writer.commit()
# for chan in changes_guessednames():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
# writer.commit()
# for chan in changes_steamreviews():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)

# for chan in change_orinames():
#     indexer.updatedoc(chan[0],chan[1],mod = "change",writer = writer,searcher = searcher)

# indexer.updatedoc(10,[("name","cs")],mod = "add",writer = writer,searcher = searcher)
# indexer.updatedoc(605140,[("name","和班尼特福迪一起攻克难关\tGetting Over It with Bennett Foddy".decode("utf8"))],mod = "change",writer = writer,searcher = searcher)

# indexer.updatedoc(321980,[("name","Hardland")],mod = "change",writer = writer,searcher = searcher)
# indexer.updatedoc(667750,[("name","Indie Friends Pack")],mod = "change",writer = writer,searcher = searcher)

writer.commit()
writer.close()
#print count

