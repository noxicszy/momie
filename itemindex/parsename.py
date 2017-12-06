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


    def nomalization(self,matri):
        for k in matri.keys():
            sm = sum(matri[k].values())
            for kk in matri[k].keys():
                matri[k][kk] = (matri[k][kk]+0.0)/sm
        return matri

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

        text = re.sub(r'\s*[a-z]*{}[a-z]*\s*'.format(name),"#",text)
        text = re.sub(r'[a-z]+',"X",text)
        text = re.sub(r'\s+'," ",text)
        return text,name
    
    def countdatabase(self,text):
        # <--backward   forward-->
        #text = self.moditext(text)
        #string has been modified only contains space as cutdown
        baca = " "
        for i in text:
            if baca != " ":
                self.formk[baca] = self.formk.get(baca,{})
                self.formk[baca][i] = self.formk[baca].get(i,0)+1
            if i !=" ":
                self.bacmk[i] = self.bacmk.get(i,{})
                self.bacmk[i][baca] = self.bacmk[i].get(baca,0)+1
            baca = i
        self.formk[baca] = self.formk.get(baca,{})
        self.formk[baca][i] = self.formk[baca].get(i,0)+1
        self.formk = self.nomalization(self.formk)
        self.bacmk = self.nomalization(self.bacmk)
        


    def tempkov(self,text):
        formk = {}
        bacmk = {}
        baca = " "
        for i in text:
            if baca != " ":
                formk[baca] = formk.get(baca,{})
                formk[baca][i] = formk[baca].get(i,0)+(1/self.formk[baca].get(i,1e-7))#####
            if i !=" ":
                bacmk[i] = bacmk.get(i,{})
                #print self.bacmk[i].get(baca,1e-7)
                bacmk[i][baca] = bacmk[i].get(baca,0)+(1/self.bacmk[i].get(baca,1e-7))
            baca = i
        formk[baca] = formk.get(baca,{})
        formk[baca][i] = formk[baca].get(i,0)+(1/self.formk[baca].get(i,1e-7))
        formk = self.nomalization(formk)
        bacmk = self.nomalization(bacmk)
        return formk,bacmk

    def generate_name(self,text,name):
        SEEDCOUNT = 10
        THREHOLD = 0.5
        #为了防止浜浜浜浜浜浜的问题，可以把中间过程中猜的名字验证到整个text中看有没有。
        text,name = self.moditext(text,name)
        #print text
        formk,bacmk = self.tempkov(text)
        answers = []

        #forward guess
        guess = sorted(formk["#"].items(),key = lambda item:item[1]) [:SEEDCOUNT]
        for i in guess:
            i = (i[0],1)
        #print"【%%】" ,guess    
        for item in guess: #直接当成栈使用得了
            tempguess = sorted(formk[item[0][-1]].items(),key = lambda item:item[1])[:SEEDCOUNT]
            
            if tempguess[0][1]<THREHOLD:  ######或者试一下前n个加到0.6的
                answers.append(item[0])
                continue
            for j in tempguess:
                if j[1]>THREHOLD:
                    if j[0]==" ":
                        answers.append(item[0])
                        continue
                    newgues = (item[0]+j[0],item[1]*j[1])
                if newgues[1]>0.01:
                    guess.append(newgues)
        #print guess
        ####################################

         #backward guess
        guess = sorted(bacmk["#"].items(),key = lambda item:item[1])[:SEEDCOUNT]
        for i in guess:
            i = (i[0],1)    
        
        for item in guess: #直接当成栈使用得了
            tempguess = sorted(bacmk[item[0][-1]].items(),key = lambda item:item[1])[:SEEDCOUNT]
            if tempguess[0][1]<THREHOLD:
                answers.append(item[0][::-1])
                continue
            for j in tempguess:
                if j[1]>THREHOLD:
                    if j[0]==" ":
                        answers.append(item[0][::-1])
                        continue
                    newgues = (item[0]+j[0],item[1]*j[1])
                if newgues[1]>0.1:
                    guess.append(newgues)
        #print guess
        ####################################
        
        return answers


        
if __name__=="__main__":
    #dik = {"aa":"bb"}
    #print dik.get("bb",0)
    mk = avmarkov(markovdir)
    trickytext = """Tricky Towers on Steam
查看此网页的中文翻译，请点击 翻译此页
With your brilliant robe and magic powers, it’s time to build some Tricky Towers! Stack your bricks in this land of f...
store.steampowered.com... 
 - 百度快照
Tricky Towers
查看此网页的中文翻译，请点击 翻译此页
Tricky Towers is a frantic physics tower building game set in a magical world.... With your brilliant robe and magic powers, it's time to build some ...
www.trickytowers.com/ 
 - 百度快照
Tricky Towerspc版下载_Tricky Towers中文版下载_游迅网
2016年12月10日 - Tricky Towers 中文版游戏类型:休闲益智 游戏语言:英文 游戏大小:70.70MB 游戏制作:WeirdBeard 游戏发行:WeirdBeard 上市时间:2016-08-05 标签: 益智 创意 ...
www.yxdown.com/SoftVie... 
 - 百度快照
tricky tower_百度图片
image.baidu.com  - 查看全部289张图片
Tricky Towers中文pc|Tricky Towers整合所有dlc下载简体中文破解...
2016年8月2日 - Tricky Towers整合所有dlc 简体中文破解版软件大小: 320M 更新时间: 2016-08-02 软件语言: 中文 软件厂商: 软件等级: 软件类别: 国产软件 / 免费软件 / ...
www.cr173.com/game/302... 
 - 百度快照
tricky tower中文版|tricky tower下载免安装硬盘版_西西游戏下载
2016年8月11日 - tricky tower,《trickytower》是一款由WeirdBeard制作发行的卡通类型的动作冒险过关游戏,游戏中玩家能体验到覅而出不错的趣味游戏体验!以物理规则为基础,核心机制是...
www.cr173.com/game/308... 
 - 百度快照
Steam 社区 :: Tricky Towers :: 成就
Tricky Towers全球成就 全球排行榜 所有玩家的百分比 总成就: 29 您必须先登录才能与这些统计进行比较 50.3% 竞赛获胜者 赢一场在线对战 40.3% 蹒跚的步履 ...
steamcommunity.com/sta... 
 - 百度快照
Tricky Tower这游戏进了哪个包啊 - 购物问题 - SteamCN 蒸汽动力 ...
4条回复 - 发帖时间: 18 Feb 2017
2017年2月18日 -  Tricky Tower这游戏进了哪个包啊[慈善包网站相关] 收藏主题 复制链接 回复 5 查看 948 收藏 0 返回列表 SOVEREIGN 27赠楼 2%赠楼率 63蒸汽 23...
https://steamcn.com/t249210-1-2 
 - 百度快照
Tricky Towers官方灌水楼【trickytowers吧】_百度贴吧
2016年11月25日 -  3回复贴,共1页 <返回trickytowers吧发表回复 发贴请遵守贴吧协议及“七条底线”贴吧投诉 停止浮动 内容: 使用签名档 查看全部 发表 保存至快速回贴...
tieba.baidu.com/p/4875... 
 - 百度快照
 tricky tower(散人试玩)|tricky tower联机版下载汉化硬盘版_西西...
2016年12月1日 - tricky tower联机版 汉化硬盘版软件大小: 320M 更新时间: 2016-12-01 软件语言: 中文 软件厂商: 软件等级: 软件类别: 国产软件 / 免费软件 / ACT动作游戏...
www.cr173.com/game/375... 
 - 百度快照
Tricky Towers on Steam
With your brilliant robe and magic powers, it’s time to build some Tricky Towers! Stack your bricks in this land of fable, whose marvelous tower ...
store.steampowered.com... 
 - 百度快照 - 翻译此页
tricky towers多少钱_百度知道

1个回答 - 提问时间: 2017年01月15日生日生命，生你妈
Remembering is a tricky businesses,We can翻译:记忆是一个复杂的业务,我们可以做到。
更多关于tricky tower的问题>>
https://zhidao.baidu.com/quest... 
 - 百度快照
Steam 上的 Tricky Towers
2016年8月2日 -  New Halloween bricks have been added for free to Tricky Towers so you can already get in the mood before October 31st - bats, pumpkins, and spiders...
store.steampowered.com... 
 - 百度快照
TrickyTowers难死塔PC硬盘版_TrickyTowers游戏下载_飞翔游戏
2016年8月22日 - 难死塔(TrickyTowers)是一款物理动作玩法的休闲益智类游戏,游戏的玩法类似于俄罗斯方块,不同的是游戏不需要消除方块,而是想办法让方块叠的更高,由于游戏没有传统...
www.fxxz.com/yx/1698..... 
 - 百度快照
俄罗斯方块大战联机|俄罗斯方块大战(Tricky Towers)Steam联机未...
2016年12月10日 -  《俄罗斯方块大战(Tricky Towers)》是一款多人竞技类游戏,融合了俄罗斯方块元素与搭积木的游戏玩法。玩家将根据随机提供的方块来搭建自己的高塔,并且能使用各种策略...
www.cr173.com/soft/380... 
 - 百度快照
Tricky Towers på Steam
New Halloween bricks have been added for free to Tricky Towers so you can already get in the mood before October 31st - bats, pumpkins, and spiders...
store.steampowered.com... 
 - 百度快照
难死塔第18关怎么过_TrickyTowers第18关视频通关攻略_快吧游戏
2016年12月16日 - TrickyTowers第18关视频通关攻略?不知道的玩家就看这边吧,小编今天给大家带来《难死塔Tricky Towers》第18关通关视频攻略,希望对玩家有所帮助。 >>>>...
pc.kuai8.com/gonglue/5... 
 - 百度快照
《Tricky Towers》中文奖杯列表
Tricky Towers 白1 金6 银8 铜13 总28 #1 Grand master wizard (宗師級巫師) 3 Tips Unlock all trophies. 解鎖所有獎盃。 0.10%珍贵度 #2 Ultimate...
d7vg.com/psngame/11...... 
 - 百度快照
《难死塔Tricky Towers》玩法说明及道具作用介绍_九游手机游戏
2016年12月19日 -  《难死塔(Tricky Towers)》是一款益智类趣味的独立休闲游戏,发布后很多玩家和小伙伴们一起进行联机体验,对于新手玩家来讲还不太熟悉游戏的玩法,下面...
www.9game.cn/news/1441... 
 - 百度快照
    """
    agetext = """Age of Empires II HD - Age of Empires
查看此网页的中文翻译，请点击 翻译此页
It is once again time to take a closer look at the history behind the civilizations in Age of Empires, and this episod...
www.ageofempires.com/g... 
 - 百度快照
Age of Empires III - Age of Empires
It is once again time to take a closer look at the history behind the  civilizations in Age of Empires, and this episode is all about the Minoan...
www.ageofempires.com/g... 
 - 百度快照 - 翻译此页
Steam 上的 Age of Empires II HD
2013年4月9日 - Age of Empires II HD《帝国时代二》经过高清重制, 拥有了新的游戏属性, 还附带了贸易卡片, 更强的AI电脑, 玩家作坊, 多人联机, 内置Steam链接和其他更多的...
store.steampowered.com... 
 - 百度快照
Age of Empires下载_单机游戏Age of Empires中文版下载_快猴游戏网
2012年7月2日 - Age of Empires,Age of Empires中文名称为帝国时代1 操作方法: 点击鼠标左键进行操作 帝国时代是无数即时策略一个很有特色的游戏,它将各个民族的历史以
www.kuaihou.com/youxi/... 
 - 百度快照
Age Of Empires_百度百科

歌曲: Age Of Empires 歌手: Epic Chorale 语言: 英语 所属专辑: Immediate Music 发行日期: 1983-03-01
生存竞赛解谜及游
baike.baidu.com/ -
生存竞赛解谜及游经典再续!《帝国时代:围攻城堡(Age of Empires: Castle Siege)》...
2014年8月26日 - 【游侠导读】微软今日正式公开了为Windows 8 PC和Windows Phone 8打造的全新游戏《帝国时代:围攻城堡(Age of Empires: Castle Siege)》。,游侠网
www.ali213.net/news/ht... 
 - 百度快照
Age of Empires II HD on Steam
《难死塔(Tricky Towers)》生存竞赛解谜及游戏性试玩心..._游民星空
    """

    text = mk.moditext(trickytext.decode('utf-8'),"tricky tower")[0]+mk.moditext(agetext.decode('utf-8'),"Age of Empires")[0]
    mk.countdatabase(text)
    #tempt,name = mk.moditext("《难死塔(Tricky Towers)》生存竞赛解谜及游戏性试玩心..._游民星空".decode('utf-8'),"tricky tower")
    
    for i in  mk.generate_name("《难死塔(Tricky Towers)》生存竞赛解谜及游戏性试玩心..._游民星空 TrickyTowers难死塔PC硬盘版_TrickyTowers游戏下载_飞翔游戏 难死塔第18关怎么过_TrickyTowers第18关视频通关攻略_快吧游戏".decode('utf-8'),"tricky tower"):
        print i


