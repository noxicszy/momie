#-^-coding:utf-8-^-
"""
NLP设想：
1.剧情——游戏介绍提取：
    利用StanfordParser，提取剧情描述中所有的语料中的主语加主要谓语的组合，连接得到词向量，进行聚类，获得一个特殊的矩阵。
    在搜索时利用关键词的主语谓语组合对，比较候选游戏结果中的剧情矩阵取最大值。
2.sentiment，游戏评价提取：
    与上述文字相似，提取形容词的组合，这样就有”角色 好“，”画质 好“之类的组合，同样是使用词向量，搜索时可以按照这些东西
    的评价排序。
搞了一个Stanford nlp可以parse中文生成依赖关系，但是调用的过程最方便的是让它处理一个文件，并且现在没有
找到一次启动然后处理好多文件的方法。然而那个东西处理句子速度还可以，但是每一次处理前的加载时间有15秒，
所以解决的办法就是把我们想要处理的文件合成一个大文件，让它去处理好了再人工解回来。
"""
import os
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
root = ""
with open("unparsedtext.txt","w")as f:
    for docnum in xrange(0, ireader.numDocs()):
        doc = ireader.document(docnum)
        review = doc.get("review")
        if review:
            review = (" .\n".decode("utf8")).join(review.split("\n"))#默认.是分句符
            f.write("\n{} 行.\n".format(doc.get("id")))
            f.write(review.encode("utf8"))

