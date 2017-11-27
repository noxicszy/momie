#!/usr/bin/env python
#-^-coding:utf-8-^-
"""
the data stored in the index system is based on pylucene.
for each game, store the fields of  main name, other names and nickname                                     name
                                    the description passages of the game for rough search                   description
                                    the 知乎里被人为归类推荐的如“有哪些适合学英语的游戏？”                          list
                                        比如用户输入了“学习英语”，呈现给用户的时候有“XXX游戏——来自知乎帖子xxxxxxxx”
                                    the 系列信息                                                              series
                                    the producer                                                            producer
                                    the vecter using "words to vector" tech for sorting (not indexed)       vector
                                    the other links and contents to present to the user
                                    images
                                    facets??
    the system should first search the naming field which is presented at the top if it exists
    then search the human arranged lists
    and search the description passages,(it would be better if we can using the synax for key words)
        using the NLP model and the game vectors to sort the list
"""
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig,Term
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

#TODO 引入log机制，记录存了的和删了的，失败了的内容

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""#####!!!!!!!WRITER 需要手动close

    def __init__(self,storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        self.store = SimpleFSDirectory(File(storeDir))
        self.analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        

        '''
        root = "tempdata"
        #self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'
        '''
        
    
    def getfieldType(self,fieldname):
        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        t3 = FieldType()
        t3.setIndexed(False)
        t3.setStored(True)
        t3.setTokenized(False)
        #t3.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)


        t1types = ["series","name"]
        t2types = ["description","list"]
        t3types = ["vector"]
        #print fieldname
        if fieldname in t1types:
        #    print "t1"
            return t1
        elif fieldname in t2types:
        #    print "t2"
            return t2
        else:
            return t3


    def indexDocs(self, root,mod="append"):
        """
        批量读取root文件夹中的JSON文件，存进pylucene
        """
        import json
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        if mod.lower()=="append":
            config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
        elif mod.lower()=="create":
            config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        else:
            raise ("the mod is illegal") #TODO: to find a better exception name

        writer = IndexWriter(self.store, config)

        failedfiles = [] #用来记录没有成功index的文件

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith('.json') and not filename.endswith('.JSON'):
                    continue
                print "adding", filename
                try:
                    path = os.path.join(root, filename)

                    with open(path,"r") as fil:
                        #print fil.readline()
                        #fil.encoding("utf-8")
                        #contents = json.loads(fil.read())
                        contents = json.load(fil)
                    
                    doc = Document()
                    for key in contents.keys():
                        print key
                        if type(contents[key]) != list:
                            contents[key] = contents[key].encode("utf-8")
                        doc.add(Field(key, str(contents[key]), self.getfieldType(key)))
                    writer.addDocument(doc)
                except Exception, e:
                    print "Failed in indexDocs:", e
                    failedfiles.append(filename)
        
        writer.commit()
        writer.close()
        print "Failed docs:",failedfiles
    
    def deletedoc(self,docvalue):
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
        writer = IndexWriter(self.store, config)
        #writer.deleteDocuments((docvalue))
        writer.deleteDocuments(Term(docvalue[0],docvalue[1]))
        print "finished"
        writer.commit()
        writer.close()
    #TODO：增加update 在已有条目的基础上添加新field

if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    #try:
    if True:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                    StandardAnalyzer(Version.LUCENE_CURRENT))
                    """
        analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
        indexer = IndexFiles( "index", analyzer)
        #indexer.indexDocs('tempdata',"create")### to make a new index, use create
        docvalue = ("name","besiege") #不用提供整个名称     “besiege 围攻”是删不掉的
        indexer.deletedoc(docvalue)
        end = datetime.now()
        print end - start
    #except Exception, e:
    #    print "Failed: ", e
    #    raise e