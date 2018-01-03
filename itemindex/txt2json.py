#-^-coding:utf-8-^-
import os
import json
import jieba
import re
import string
"""
change the txt files into json ones 
parse the file by the way
"""
errors = []

def nameparser(name):
    punctuation = (string.punctuation+"‘（）。，、；’【、】`～！￥%……&×——+=-|：”《》？,™,の,®").decode('utf-8')
    tempname = ""
    name = name.decode("utf8")
    for i in range(len(name)):
        if name[i] not in punctuation:
            tempname+=name[i]
    return tempname.encode("utf8")

def contentparser(cont):
    #print type(cont)
    try:
        cont = " ".join(jieba.cut(cont))
    except:
        print cont
        errors.append(cont)
        return ""
    return cont.encode("utf8")

root = "../datastore/basic_info"
targetroot = "../datastore/json_info"
for root, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if True:
            path = os.path.join(root, filename)
            with open(path,"r") as f:
                game = {}
                isreviews = False
                for line in f.readlines():
                    #line = line.decode("utf8")
                    if not isreviews:
                        line  = line.split()
                        if line[0]=="appid:":
                            game["id"] = int(line[1])
                        elif line[0]=="appname:":
                            game["name"] = nameparser(" ".join(line[1:]))
                        elif line[0]=="apptags:":
                            game["tags"] = " ".join(line[1:])
                        elif line[0]=="appdevelopers:":
                            game["producer"] = " ".join(line[1:])
                        elif "reviews:" in line:
                            isreviews = True
                            game["review"] = ""
                    else:
                        #print 'helre'
                        game["review"]= game["review"]+line+" "
            path = os.path.join(targetroot,filename+".json")
            game["review"] = contentparser(game["review"])
            if  game["review"] =="" :
                del(game["review"])
            print game["id"] 
            with open(path,"w") as f:
                json.dump(game,f,ensure_ascii=False)

with open("errors.txt","w")as f:
    f.writelines(errors)

                                
