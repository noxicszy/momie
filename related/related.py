# -*- coding: utf-8 -*-
import re
import os
import jieba
import vsm_cosine_similarity as vsm
import gensim
# 导入模型
def jaccard_similarity(x,y):
    intersection_cardinality = len(set.intersection(*[set(x),set(y)]))
    union_cardinality = len(set.union(*[set(x),set(y)]))
    if union_cardinality == 0:
        return 0
    return intersection_cardinality/float(union_cardinality)
counts = 1
root = "basic_info"
list1 = os.listdir(root)
for j in range(0,len(list1)):
    path = os.path.join(root,list1[j])
    if os.path.isfile(path):
        value_list={}
        appid=''
        appname =''
        apptags=''
        appdevelopers=''
        file1 = open(path)
        b= file1.read().decode('utf-8')
        appid = re.findall(r"appid\: (.+?)\n", b)[0].strip()
        ff = "related_games/"+ appid
        if os.path.isfile(ff):
            print counts
            counts += 1
            continue
        appname = re.findall(r"appname\: (.+?)\n", b)[0].strip()
        try:
            apptags = re.findall(r"apptags\: (.+?)\n", b)[0].strip()
            tags_list = apptags.split("\t")
        except:
            tags_list = []
        try:
            appdevelopers = re.findall(r"appdevelopers\: (.+?)\n", b)[0].strip()
        except:
            appdevelopers = ''
        try:
            reviews = re.findall(r"reviews\: \n(.*)", b)[0].strip()
        except:
            reviews = ''
        for i in range(0,len(list1)):
            path2 = os.path.join(root,list1[i])
            if os.path.isfile(path2):
                appid2=''
                appname2 =''
                apptags2=''
                appdevelopers2=''
                file2 = open(path2)
                b2= file2.read().decode('utf-8')
                appid2 = re.findall(r"appid\: (.+?)\n", b2)[0].strip()
                appname2 = re.findall(r"appname\: (.+?)\n", b2)[0].strip()
                try:
                    apptags2 = re.findall(r"apptags\: (.+?)\n", b2)[0].strip()
                    tags_list2 = apptags2.split("\t")
                except:
                    tags_list2 = []
                try:
                    appdevelopers2 = re.findall(r"appdevelopers\: (.+?)\n", b2)[0].strip()
                except:
                    appdevelopers2 = ''
                try:
                    reviews2 = re.findall(r"reviews\: \n(.*)", b2)[0].strip()
                except:
                    reviews2 =''
                if len(reviews)>0:
                    lis1 = []
                    l1 = jieba.cut(reviews)
                    for k in l1:
                        lis1.append(k)
                    if len(reviews2)>0:
                        lis2 = []
                        l2 = jieba.cut(reviews2)
                        for k in l2:
                            lis2.append(k)
                        re_value = vsm.vsm2(lis1,lis2)
                    else:
                        re_value = 0
                else:
                    re_value = 0
                name_value = vsm.vsm(appname,appname2)
                tag_value=jaccard_similarity(tags_list,tags_list2)
                if appdevelopers == appdevelopers2:
                    dev_value = 0.3
                else:
                    dev_value = 0
                value = 1.3*name_value+re_value+tag_value+dev_value
                value_list[appid2]=value
        dic = sorted(value_list.iteritems(), key = lambda asd:asd[1], reverse = True)
        respath = "related_games/"+ appid
        res = open(respath,'wb')
        res.write("appid: ")
        res.write(appid.encode('utf-8'))
        res.write('\n')
        res.write("appname: ")
        res.write(appname.encode('utf-8'))
        res.write('\n')
        res.write("related games: ")
        count =0
        for item in dic:
            if count < 6:
                res.write(item[0].encode('utf-8'))
                res.write('\t')
                count += 1
            else:
                break
        res.close()
        print counts
        counts += 1
            
