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
    for i in content.items():
        print " ".join(jieba.cut(i[1]))
        yield int(i[0]),[("name",i[1].decode("utf8")),("names"," ".join(jieba.cut(i[1])))] 

def changes_guessednames():
    with open("../datastore/filtedguess.pkl" ,"rb") as f:
         content = pickle.load(f)
    for i in content:
        print " ".join(jieba.cut(i[1]))
        yield i[0],[("names"," ".join(jieba.cut(i[1])))] 

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

     

# for chan in changes_nlpvector():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)

# for chan in changes_similargames():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
#     print chan[0],chan[1]

# for chan in changes_name():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)

# for chan in changes_guessednames():
#     indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
for chan in changes_steamreviews():
    indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer,searcher = searcher)
    # print chan

# indexer.updatedoc(10,[("name","cs")],mod = "add",writer = writer,searcher = searcher)

writer.commit()
writer.close()
#print count

