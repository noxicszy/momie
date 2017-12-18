#-^-coding:utf-8-^-
import os
import json
root = "basic_info"
targetroot = "json_info"
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
                            game["name"] = " ".join(line[1:])
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
            #print game
            with open(path,"w") as f:
                json.dump(game,f,ensure_ascii=False)
            break


                                
