# from gameindexer import IndexFiles
# import gameindexer
import os
import pickle
# gameindexer.lucene.initVM(vmargs=['-Djava.awt.headless=true'])
# print 'lucene', gameindexer.lucene.VERSION
# analyzer = gameindexer.SimpleAnalyzer(gameindexer.Version.LUCENE_CURRENT)
# #--------------------------------------#
# indexer = IndexFiles( "index", analyzer)
# #--------------------------------------#
# config = gameindexer.IndexWriterConfig(gameindexer.Version.LUCENE_CURRENT, analyzer)
# config.setOpenMode(gameindexer.IndexWriterConfig.OpenMode.APPEND)
# writer = gameindexer.IndexWriter(indexer.store, config)

def changes_nlpvector():
    root = "../datastore/vector_info"
    for root, dirnames, filenames in os.walk(root):
        for filename in filenames:
            path = os.path.join(root, filename)
            contents = []
            with open(path,"rb") as f:
                contents = pickle.load(f)
            for i in contents.items():
                yield (i[0],[("vector",str(i[1]))])


def changes_similargames():
    root = "../datastore/related_games/related_games"
    for fil in os.listdir(root):
        with open(os.path.join(root,fil),"r",encoding="utf8") as f:
            try:
                appid = int(f.readline().split()[1])
                f.readline()
                related = " ".join(f.readline().split()[2:])
                yield (appid,[("related",related)])
            except Exception as e:
                print (fil,e)

# for chan in changes_nlpvector():
    # indexer.updatedoc(chan[0],chan[1],mod = "add",writer = writer)

# writer.commit()
    
for chan in changes_similargames():
    print(chan)


