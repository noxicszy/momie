#encoding=utf-8
import lucene
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.util import BytesRef, BytesRefIterator, Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import Term
from org.apache.lucene.index import \
    IndexWriterConfig, IndexWriter, DirectoryReader

if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

directory = RAMDirectory()
analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
iconfig = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
iwriter = IndexWriter(directory, iconfig)

ft = FieldType()
ft.setIndexed(True)
ft.setStored(True)
ft.setTokenized(True)
ft.setStoreTermVectors(True)
ft.setStoreTermVectorOffsets(True)
ft.setStoreTermVectorPositions(True)

countlines = 0
with open("nameguess.txt","r") as f:
    for line in f.readlines():
        doc = Document()
        doc.add(Field("words", line, ft))
        countlines+=1
        iwriter.addDocument(doc)

iwriter.commit()
iwriter.close()

ireader = DirectoryReader.open(directory)

with open("filtedguess.txt","w") as f:
    for docnum in xrange(0, countlines):
        doc = ireader.document(docnum)
        words = doc.get("words")
        #print "{]", words
        filtedwords = []
        for word in words.split():
            #print word
            if ireader.docFreq(Term("words",word))<=2:
                print word
                filtedwords.append(word.encode("utf8"))
        f.write(" ".join(filtedwords)+"\n")