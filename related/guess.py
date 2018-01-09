# -*- coding: utf-8 -*-
import re
import os
import random

def guess(a):
    if (len(a)==0):
        res = []
        root = "related_games"
        list1 = os.listdir(root)
        for i in range(10):
            rd=random.randint(0, 30000)
            if (str(list1[rd]) in a):
                rd=random.randint(0, 30000)
            a.append(str(rd))
            res.append(str(list1[rd]))
        return res
    res = []
    f = "related_games/"+a[0]
    fl = open(f)
    content = fl.read()
    r = re.findall(r"related games\: (.*)", content)[0].strip()
    inter = r.split("\t")[1:]
    for i in range(len(a)):
        ff = "related_games/"+ a[i]
        file1 = open(ff)
        content1 = file1.read()
        related = re.findall(r"related games\: (.*)", content1)[0].strip()
        related_set = related.split("\t")[1:]
        for j in range(i+1,len(a)):
            f = "related_games/"+a[j]
            fl = open(f)
            content = fl.read()
            r = re.findall(r"related games\: (.*)", content)[0].strip()
            inter = r.split("\t")[1:]
            inter = set.intersection(*[set(inter),set(related_set)])
            res = set.union(*[set(inter),set(res)])
    res = list(res)
    required_more = 10 - len(res)
    root = "related_games"
    list1 = os.listdir(root)
    for i in range(required_more):
        rd=random.randint(0, 30000)
        if (str(list1[rd]) in a):
            rd=random.randint(0, 30000)
        a.append(str(rd))
        res.append(str(list1[rd]))
    return res
