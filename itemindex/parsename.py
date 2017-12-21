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
import os
import math
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
    def save(self,stordir):
        data = [self.formk,self.bacmk]
        with open(stordir,'wb') as f:
            pickle.dump(data, f)

    def nomalize(self):
        self.nomalization(self.formk)
        self.nomalization(self.bacmk)

    def nomalization(self,matri):
        for k in matri.keys():
            sm = sum(matri[k].values())
            for kk in matri[k].keys():
                #assert matri[k][kk]!=0.0
                
                matri[k][kk] = float(matri[k][kk])/sm
                if matri[k][kk]==0.0:
                    print k ,kk ,"ZERO"
                    del matri[k][kk]


    def moditext(self,text,name):
        #find the name and replace the name with # 
        #replace the punctuations and the writespaces with space
        #replace the english letter with X
        text  = text.lower()
        name = name.lower()
        punctuation = (string.punctuation+"‘（）。，、；’【、】`～！￥%……&×——+=-|：”《》？").decode('utf-8')
        #print punctuation
        # text = re.sub(r'[{}]+'.format(punctuation)," ",text) #为什么把英文字母也去掉了？
        for i in range(len(text)):
            if text[i] in punctuation:
                text = text[:i] + ' ' + text[i+1:]
        #name = re.sub(r'[{}]+'.format(string.punctuation)," ",name)
        for i in range(len(name)):
            if name[i] in punctuation:
                name = name[:i] + ' ' + name[i+1:]
        #print "[***]",name,"3#",text
        text = re.sub(r'\s+'," ",text)
        name = re.sub(r'\s+'," ",name)
        concession = 1  #让步 要不然没有搜索结果了
        text = re.sub(r'\s*[a-z]*{}[a-z]*\s*'.format(name),"#",text)
        text = re.sub(r'\s*[a-z]*{}[a-z]*\s*'.format("".join(name.split())),"#",text)
        while "#" not in text and concession<5:
            print "concession",concession 
            for i in range(concession):
                target  = " ".join(name.split()[i:-1-i])
                text = re.sub(r'\s*[a-z]*{}[a-z]*\s*'.format(target),"#",text)
            concession +=1
        
        
        #text = re.sub(r'[a-z]+',"X",text)
        text = re.sub(r'#+',"#",text)
        text = re.sub(r'\s+'," ",text)
        if not "#" in text:
            print "ERROR"# name, text

        return text,name
    
    def sliceintowords(self,text):
        #return a list which split every chinese character and every english word
        temptext = []
        a = 0
        b = 0
        while b<len(text)-1:
            if text[b] in string.letters:
                b +=1
            else :
                if a==b:
                    temptext.append(text[a:b+1])
                else:
                    temptext.append(text[a:b])
                b +=1
                a = b
        if a==b :
            #print text[a:b+1]
            temptext.append(text[a:b+1])
        else:
            temptext.append(text[a:b])
        #print "yes"
        return temptext

    def countdatabase(self,text):
        # <--backward   forward-->
        #text = self.moditext(text)
        #string has been modified only contains space as cutdown
        temptext = self.sliceintowords(text)
                
        baca = " "
        tempform = {}
        tempback = {}

        for i in temptext:
            if baca != " ":
                # self.formk[baca] = self.formk.get(baca,{})
                # self.formk[baca][i] = self.formk[baca].get(i,0)+1
                tempform[baca] = tempform.get(baca,set())
                tempform[baca].add(i)
            if i !=" ":
                # self.bacmk[i] = self.bacmk.get(i,{})
                # self.bacmk[i][baca] = self.bacmk[i].get(baca,0)+1
                tempback[i] = tempback.get(i,set())
                tempback[i].add(baca)
            baca = i
        # tempform[baca] = tempform.get(baca,{})
        # tempform[baca][" "] = tempform[baca].get(" ",0)+1
        tempform[baca] = tempform.get(baca,set())
        tempform[baca].add(i)
        for i in tempform.keys():
            for j in tempform[i]:
                self.formk[i] = self.formk.get(i,{})
                self.formk[i][j] = self.formk[i].get(j,0)+1
        for i in tempback.keys():
            for j in tempback[i]:
                self.bacmk[i] = self.bacmk.get(i,{})
                self.bacmk[i][j] = self.bacmk[i].get(j,0)+1
                
        # self.formk = self.nomalization(self.formk)
        # self.bacmk = self.nomalization(self.bacmk)#大bug 不能每回都nomalazation！！！
        
        

    def wordlenth(self,text):
        lenth  = len(text)
        text =text + " "
        for i in range(lenth):
            if text[i] in string.letters and text[i+1]in string.letters:
                lenth-=1
        return lenth

    def tempkov(self,text):
        formk = {}
        bacmk = {}
        baca = " "
        temptext = self.sliceintowords(text)
        for i in temptext:
            if baca != " ":
                formk[baca] = formk.get(baca,{})
                if  not self.formk[baca].get(i,1):
                    print baca,i,self.formk[baca].get(i)
                formk[baca][i] = formk[baca].get(i,0)+(1/(self.formk[baca].get(i,0)+1e-10))#####
            if i !=" ":
                bacmk[i] = bacmk.get(i,{})
                #print self.bacmk[i].get(baca,1e-7)
                bacmk[i][baca] = bacmk[i].get(baca,0)+(1/(self.bacmk[i].get(baca,0)+1e-10))
            baca = i
        formk[baca] = formk.get(baca,{})
        formk[baca][" "] = formk[baca].get(" ",0)+(1/(self.formk[baca].get(" ",0)+1e-10))


        self.nomalization(formk)
        self.nomalization(bacmk)
        # for i in formk["#"].keys():
        #     print i,formk["#"][i]
        # print (formk["#"])

        return formk,bacmk
    
    def lastword(self,text):
        if text[-1] not in string.letters:
            return text[-1]
        i = -1
        while -i<=len(text) and text[i] in string.letters :
            i-=1
        return text[i+1:]

    def generate_name(self,text,name):
        SEEDCOUNT = 10
        THREHOLD = 0.01

        #为了防止浜浜浜浜浜浜的问题，可以把中间过程中猜的名字验证到整个text中看有没有。
        #text,name = self.moditext(text,name)
        #print text
        formk,bacmk = self.tempkov(text)
        answers = []

        #forward guess
        guess = sorted(formk["#"].items(),key = lambda item:item[1],reverse=True) [:SEEDCOUNT]
        
        for i in range(len(guess)):
            guess[i] = (guess[i][0],0)
        
        #print"【%%】" ,guess    
        for item in guess: #直接当成栈使用得了
            try:
            #if True:
                if len(formk[self.lastword(item[0])].items())>SEEDCOUNT:
                    tempguess = sorted(formk[self.lastword(item[0])].items(),key = lambda item:item[1],reverse=True)[:SEEDCOUNT]
                else:
                    tempguess = sorted(formk[self.lastword(item[0])].items(),key = lambda item:item[1],reverse=True)
            except:
                print "except in GENERATENAME"
                if self.wordlenth(item[0])>1:
                    answers.append(item[0])
                continue
            if tempguess[0][1]<=THREHOLD:  ######或者试一下前n个加到0.6的
                if self.wordlenth(item[0])>1:
                    answers.append(item[0])
                continue
            for j in tempguess:
                #print item[0].encode("utf8"),item[1] ,j[0].encode("utf8"),j[1]
                if j[1]>THREHOLD:
                    if j[0]==" ":
                        if self.wordlenth(item[0])>1:
                            answers.append(item[0])
                        continue
                    newgues = (item[0]+j[0],item[1]+math.log(j[1]))

                    if not  item[1]+math.log(j[1])>0:
                        print math.log(j[1]),j[1]

                    if newgues[1]>-0.01 and self.wordlenth(newgues[0])<10:
                        guess.append(newgues)
                    else:
                        if self.wordlenth(newgues[0])>1:
                            answers.append(newgues[0])

        # for i in guess:
        #     print i[0].encode("utf8"),i[1]


        #print guess
        ####################################

         #backward guess
        guess = sorted(bacmk["#"].items(),key = lambda item:item[1],reverse=True)[:SEEDCOUNT]
        #print guess
        for i in range(len(guess)):
            
            guess[i] = (guess[i][0],0)
        
        for item in guess: #直接当成栈使用得了
            try:
                tempguess = sorted(formk[self.lastword(item[0])].items(),key = lambda item:item[1],reverse=True)[:SEEDCOUNT]
            except:
                if self.wordlenth(item[0])>1:
                    answers.append(item[0])
                continue
            if tempguess[0][1]<THREHOLD:
                if self.wordlenth(item[0])>1:
                    answers.append(item[0])
                continue
            for j in tempguess:
                if j[1]>THREHOLD:
                    if j[0]==" ":
                        if self.wordlenth(item[0])>1:
                            answers.append(item[0])
                        continue
                    newgues = (item[0]+j[0],item[1]+math.log(j[1]))
                    if newgues[1]>0.1and self.wordlenth(newgues[0])<10:
                        guess.append(newgues)
        #print guess
        ####################################
        result = []
        for wd in answers:
            if wd in text:
                result.append(wd)
        return result

    def avprobablity(self,word):
        #return the average probablity of the apperence of a word using the average markov
        fscore = 0
        bscore = 0
        baca = "#"
        #print self.sliceintowords(word)
        for i in self.sliceintowords(word):
            #try:
            fscore+=math.log(self.formk[baca][i])
            
            #bscore+=math.log(self.bacmk[baca][i])
            #print baca,i,self.formk[baca][i]
            baca = i
            #except:
                #print "error in avprobablity"
                #return 0 , 0
        return fscore,bscore
        
if __name__=="__main__":
    #dik = {"aa":"bb"}
    #print dik.get("bb",0)
    mk = avmarkov(markovdir)
    root = "../webfetch/baidu_zhName/baidu_result"
    data = {}

    for root, dirnames, filenames in os.walk(root):
        for filename in filenames:
                if not filename.endswith('.txt'):
                    continue
                print "adding", filename
                try:
                    path = os.path.join(root, filename)
                    with open(path) as file:
                        name = file.readline().strip()
                        contents = unicode(file.read(),"utf-8")
                        con,nam = mk.moditext(contents,name)
                        data[nam] =(filename[:-4],con)
                        mk.countdatabase(con)
                        
                except Exception, e:
                    print "Failed in indexDocs:", e
    ####！！！！！！注意进行下一步前手动nomalazation！！！！
    mk.nomalize()
    mk.save(markovdir)

    #tempt,name = mk.moditext("《难死塔(Tricky Towers)》生存竞赛解谜及游戏性试玩心..._游民星空".decode('utf-8'),"tricky tower")

    # for i in  mk.generate_name("《难死塔(Tricky Towers)》生存竞赛解谜及游戏性试玩心..._游民星空 TrickyTowers难死塔PC硬盘版_TrickyTowers游戏下载_飞翔游戏 难死塔第18关怎么过_TrickyTowers第18关视频通关攻略_快吧游戏".decode('utf-8'),"tricky tower"):
    #     print i
    #print data.keys()

    #print mk.generate_name(data["Railroad X"][1],data["Railroad X"][0])

    # with open(os.path.join(root,"109200.txt"))as f:
    #     name = f.readline().strip()
    #     contents = unicode(f.read(),"utf-8")
    #     con,nam = mk.moditext(contents,name)
    #     data[nam] =con
    # print data.keys()
    # print data["legend of fae"].encode("utf8")
    # res = mk.generate_name(data["legend of fae"],"legend of fae")

    # for a in res:
    #     #>>>>>>>>>>>>>>>>>>>>>>筛选在别的地方出现过的重复 暴搜或者放到lucene里找一遍 <<<<<<<<<<<<<<<<<<<<
    #     print a.encode("utf8")

    # print mk.avprobablity("仙境".decode("utf8"))
    #print mk.wordlenth("abdd绿色".decode("utf8"))
    # print mk.avprobablity("很像".decode("utf8"))
    # print mk.avprobablity("真tm".decode("utf8"))

    with open("nameguess.txt","w") as f:

        for game in data.items():
            try:
                res = mk.generate_name(game[1][1],game[0])
                if res:
                    names = [a.encode("utf-8")  for a in res]
                    f.write(game[1][0]+" "+game[0]+"\t"+"\t".join(names)+"\n")
            except:
                print game[0].encode("utf-8")
        


