#-^-coding:utf-8-^-
import re
"""
利用LSH方法，主要分为两个部分，第一个是存储所有的名字到bucket里面，第二个是利用bucket的初步hash功能，来寻找可能长得像的词条，
最后再计算嫌疑词条和query词条的edit distance. 得到最终的疑似词条。
为了避免多次加载，把数据存到datastore里面。！！！记得要手动更新名字集
"""

class QueryCorrecter():
    def __init__(self):
        self.keys = []
        self.buckets = []
        pass

    def hashvalue(self,p,c,d):
        # #p:d dimension integer vector list
        # #c:the wei
        # #d:取的位 从1开始
        res = []
        for dd in d:
            dd -=1
            i = dd/c
            if p[i]>dd%c:
                res.append(1)
            else: 
                res.append(0)
        return res

    def calvec(self,text,d):
        """
        很难找到特征，目前解决方案：将整个单词长度分为2份，字母表按长度分为13份。统计个数，生成52维整数向量
        取其中的13维，这样平均一个bucket四个左右，再变成hamming数
        """
        text = re.sub(r'\d+',"",text)
        print text
        vector = []
        a = len(text)/2
        for i in range(2):
            tempvec = [0]*13
            for j in range(a):
                tempvec[ord(text[i*a+j])%13]+=1 #TODO：此处是%还是/有待讨论
            vector +=tempvec
        #print len(vector)

        return self.hashvec2num(self.hashvalue(vector,2,d))

    def hashvec2num(self,vec):
        num = 0
        for i in vec:
            num = num*2+i
        return num
                
correcter = QueryCorrecter()
# while True:
#     print correcter.calvec(raw_input(),[1,5,8,13,18,24,26,30,33,39,41,46,51])


