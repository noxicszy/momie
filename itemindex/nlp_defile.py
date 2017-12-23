#-^-coding:utf-8-^-
import re
import json
FIL = "parsedtext.txt"
with open(FIL,"r")as f:
    gameid = None
    data = {"v":[],"n":[]}
    for line in f.readlines():
        if line    and gameid:
            with open("tuplewords{}".format(gameid),"r")as out:
                json.dump(data,out,ensure_ascii=False)
        elif line :
            data[""].append()
            