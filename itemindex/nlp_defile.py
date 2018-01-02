#-^-coding:utf-8-^-
import re
import os
"""
多语言通用
需要提取的词汇组合实例：
nsubj(建-38, 机场-37)
dobj(支持-20, 中文-21) 这句话前面是 ccomp(希望-17, 支持-20)
nsubj(碰撞-66, 飞机-62)
nsubj(好-6, 画质-4)
nsubj(过瘾-13, 画质-1)
nsubj(好-16, 剧情-14)

nsubj(一般-15, 屎-14)
amod(画质-17, 一般-15) 画质一般 和 画质屎一般 含义差不多

amod(游戏-4, 好-3)
amod(画质-8, 无聊-2)
dobj(好-10, 内容-15)
ccomp(解密-7, 好玩-11)

nsubj(risen-8, Empire-2) 原文：升阳帝国东方崛起
nmod(Seas-3, Command-1)

dep(行-37, 709174-36)
"""
import re
import json
FIL = "parsedtext.txt"
stordir = "../datastore/duple_words"
with open(FIL,"r")as f:
    gameid = None
    data = {"nsubj":[],"amod":[],"dobj":[]}
    for line in f.readlines():
        line = line.strip()
        print line.decode("utf8")
        if line.split("-")[0]=='dep(行': 
            newid = re.findall(r", (\d+)-",line)
            if not len(newid):
                continue
            if gameid :
                with open(os.path.join(stordir,"tuplewords_{}.json").format(gameid),"w")as out:
                    json.dump(data,out,ensure_ascii=False)
            gameid = int(newid[0])
            data = {"nsubj":[],"amod":[],"dobj":[]}
        elif line.split("(")[0]=="nsubj":
            # print re.findall(r"\((.+?)-",line)
            # print re.findall(r"\((.+?)-",line)[0]
            data["nsubj"].append((re.findall(r", (.+)-",line)[0],re.findall(r"\((.+?)-",line)[0]))
        elif line.split("(")[0]=="amod" :
            data["amod"].append((re.findall(r"\((.+?)-",line)[0],re.findall(r", (.+?)-",line)[0]))
        elif line.split("(")[0]=="dobj" :
            data["dobj"].append((re.findall(r"\((.+?)-",line)[0],re.findall(r", (.+?)-",line)[0]))
    with open(os.path.join(stordir,"tuplewords_{}.json").format(gameid),"w")as out:
                json.dump(data,out,ensure_ascii=False)

            