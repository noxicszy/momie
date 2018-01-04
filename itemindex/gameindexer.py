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
                                                                                                            id
                                                                                                            tags
                                                                                                            review
                                    images
                                    facets??
    the system should first search the naming field which is presented at the top if it exists
    then search the human arranged lists
    and search the description passages,(it would be better if we can using the synax for key words)
        using the NLP model and the game vectors to sort the list

2017-12-18 新增
            TODO：利用nltk的maxentropy 训练sentiment analysis
            TODO：利用Stanford的pos tagging 寻找语料中的动宾词汇对，添加到向量中
"""
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import SimpleAnalyzer,WhitespaceAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType,IntField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig,Term
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import NumericRangeQuery
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
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
        #self.dir = storeDir
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
    
    # def getanalyzer(self,fieldname):
    #     t1types = ["series","name"]
    #     t2types = ["description","list"]
    #     t3types = ["vector"]
    #     if fieldname in t1types:
    #         #    print "t1"
    #         analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
    #         return analyzer
    #     # elif fieldname in t2types:
    #     #     analyzer = SimpleAnalyzer((Version.LUCENE_CURRENT))
    #     #     return analyzer
    #     else :
    #         return None
        
    
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

        t1types = ["series","name","tags","producer"]
        t2types = ["description","list","review"]
        t3types = ["vector"]
        #print fieldname
        if fieldname in t1types:
        #    print "t1"
            return t1
        elif fieldname in t2types:
        #    print "t2"
            return t2
        elif fieldname=="id":
            t4 = FieldType()
            t4.setIndexed(True)
            t4.setStored(True)
            t4.setNumericType(FieldType.NumericType.INT)
            return t4
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
                #try:
                if True:
                    path = os.path.join(root, filename)

                    with open(path,"r") as fil:
                        #print fil.readline()
                        #fil.encoding("utf-8")
                        #contents = json.loads(fil.read())
                        contents = json.load(fil)
                    doc = Document()
                    for key in contents.keys():
                        #print key
                        if type(contents[key]) == int:
                            doc.add(IntField(key, contents[key], self.getfieldType(key)))
                        else:
                            if type(contents[key]) != list: 
                                contents[key] = contents[key].encode("utf-8")
                            # ana = self.getanalyzer(key)
                            # if ana:
                            doc.add(Field(key, str(contents[key]), self.getfieldType(key)))
                    #print contents["id"]
                    writer.deleteDocuments(NumericRangeQuery.newIntRange("id", int(contents["id"]), int(contents["id"]), True, True))
                    writer.addDocument(doc)
                # except Exception, e:
                #     print "Failed in indexDocs:", e
                #     failedfiles.append(filename)
        
        writer.commit()
        writer.close()
        print "Failed docs:",failedfiles
    
    def deletedoc(self,docvalue,writer = None):
        opened = False
        if writer == None:
            opened = True
            config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
            config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
            writer = IndexWriter(self.store, config)
        #writer.deleteDocuments((docvalue))
        #writer.deleteDocuments(Term(docvalue[0],docvalue[1]))
        writer.deleteDocuments(NumericRangeQuery.newIntRange("id", 11111, 11111, True, True))
        print "delete finished"
        if opened:
            writer.commit()
            writer.close()
    #TODO：增加update 在已有条目的基础上添加新field
    
    def updatedoc(self,appid,updates,mod = "add",writer = None):
        #the format of the updates:
        #[(field 1,value 1),().....]
        opened = False
        if writer == None:
            opened = True
            config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
            config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
            writer = IndexWriter(self.store, config)

        searcher = IndexSearcher(DirectoryReader.open(self.store))

        query = NumericRangeQuery.newIntRange("id", appid, appid, True, True)
        scoreDocs = searcher.search(query, 50).scoreDocs
        if not scoreDocs:
            print appid,"not found"
            if opened:
                writer.close()
            return
        doc = searcher.doc(scoreDocs[0].doc) 
        
        for key,value in updates:
            if mod=="add" and key!="vector" and key!="id":
                old = doc.get(key)
                if  old:
                    value += " "+doc.get(key)
            doc.removeField(key)
            doc.add(Field(key,value, self.getfieldType(key))) 
            # java.lang.IllegalArgumentException: can only update NUMERIC or BINARY fields! field=name 内置updates不好用
        writer.deleteDocuments(NumericRangeQuery.newIntRange("id", appid, appid, True, True))
       
        doc.removeField("id")
        doc.add(IntField("id", appid, self.getfieldType("id"))) #实验证明id字段要重新添加，否则会变成unicode格式 日狗了
        writer.addDocument(doc)
        print appid,"update finished"
        if opened:
            writer.commit()
            writer.close()
    
    

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

        """
        关于analyzer：
        standardanalyzer会把中文汉字都切开
        simpleanalyzer会把数字词去掉 如2048 但是数字只要前面有字母就不会被切，有标点也不行如 圣杯战争:2048
                                        解决方法：把标题里面带有数字的全都前面加上字母 索引关键词 圣杯战争:a2048
                                        对于搜索a2048 以及搜索 圣杯战争 有效。 但是直接搜索 圣杯战争:a2048 还是不会出来结果
                                        所以直接去掉标点符号吧 圣杯战争2048
        """
        analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
        indexer = IndexFiles( "index", analyzer)
        #indexer.indexDocs('../datastore/json_info',"create")### to make a new index, use create
        # docvalue = ("name","besiege") #不用提供整个名称     “besiege 围攻”是删不掉的
        # indexer.deletedoc(docvalue)
        #indexer.updatedoc(446640,[("vector","11111111")])
        end = datetime.now()
        print end - start
    #except Exception, e:
    #    print "Failed: ", e
    #    raise e