cd /yangcy/NLP/stanford-segmenter-2015-12-09/
for i in ./nlp_raw/*.txt
do
echo $i
./segment.sh ctb $i UTF-8 0 > /yangcy/NLP/stanford-parser-full-2017-06-09/${i:1}
# echo /yangcy/NLP/stanford-parser-full-2017-06-09/${i:2}
done

cd /yangcy/NLP/stanford-parser-full-2017-06-09/
for i in ./nlp_raw/*.txt
do
echo $i
java -Xmx6g -cp "*" edu.stanford.nlp.parser.nndep.DependencyParser     -model edu/stanford/nlp/models/parser/nndep/UD_Chinese.gz     -tagger.model edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger     -textFile $i -outFile tdata/${i:9}
# echo -Xmx6g -cp "*" edu.stanford.nlp.parser.nndep.DependencyParser     -model edu/stanford/nlp/models/parser/nndep/UD_Chinese.gz     -tagger.model edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger     -textFile $i -outFile tdata/${i:10}
done