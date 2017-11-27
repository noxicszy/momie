#-^-coding:utf-8-^-
"""
使用markov猜测游戏别名
处理百度游戏名搜索结果
假设百度词条结果中一定会有别名紧挨着游戏名的词条。
总体是利用了贝叶斯公式，计算P（xx是别名|xx出现在搜索结果中）的最大值。
    化简以后就剩下了比较 p（本词条mar）/p（平均mar）的乘机的最大值
"""
import pickle
import re
import string
markovdir = "../datastore/markovdata.kov"
class avmarkov:
    def __init__(self,stordir):
        data = []
        try:
            with open(stordir,'rb') as f:
                data = pickle.load(f)
        except:
            print "initiated a new file"
        if data == []:
            self.formk={}
            self.bacmk={}
        else:
            self.formk = data[0]
            self.bacmk = data[1]
    
    def countdatabase(self,string):
        # <--backward   forward-->
        #string has been modified only contains space as cutdown
        baca = " "
        for i in string:
            if baca != " ":
                self.formk[baca] = self.formk.get(baca,{})
                self.formk[baca][i] = self.formk[baca].get(i,0)+1
            if i !=" ":
                self.bacmk[i] = self.bacmk.get(i,{})
                self.bacmk[i][baca] = self.bacmk[i].get(baca,0)+1
            baca = i
        self.formk[baca] = self.formk.get(baca,{})
        self.formk[baca][i] = self.formk[baca].get(i,0)+1

    def moditext(self,text,name):
        #find the name and replace the name with # 
        #replace the punctuations and the writespaces with space
        #replace the english letter with X
        text  = text.lower()
        name = name.lower()
        punctuation = (string.punctuation+"‘（）。，、；’【、】`～！￥%……&×——+=-|：”《》？").decode('utf-8')
        print punctuation
        # text = re.sub(r'[{}]+'.format(punctuation)," ",text) #为什么把英文字母也去掉了？
        for i in range(len(text)):
            if text[i] in punctuation:
                text = text[:i] + ' ' + text[i+1:]
        name = re.sub(r'[{}]+'.format(string.punctuation)," ",name)
        output = open('output.txt', 'w')
        output.write(text.encode('utf-8'))
        print name #TODO:把punctual换成 带有中文的
        
if __name__=="__main__":
    #dik = {"aa":"bb"}
    #print dik.get("bb",0)
    mk = avmarkov(markovdir)
    #mk.countdatabase("总体是利用 了贝叶斯公式，计算P（xx是别名|xx出现在 搜索结果中）的最大值。".decode("utf8"))
    mk.moditext("总体是利用 了贝叶斯公式，计算P（xx是别名|xx出现在 搜索结果中）的最大值。".decode('utf-8'),"tricky-tower")
    #print mk.formk
    #print mk.bacmk


