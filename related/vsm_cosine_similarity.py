# -*- coding: utf-8 -*-
import time          
import re          
import os
import string
import sys
import math

def CountKey1(list1):
    try:
        table = {}
        for word in list1:
            if word!="" and table.has_key(word):
                num = table[word]
                table[word] = num + 1
            elif word!="":
                table[word] = 1

        #键值从大到小排序
        dic = sorted(table.iteritems(), key = lambda asd:asd[1], reverse = True)
        return dic
        
    except Exception,e:    
        print 'Error:',e

''' ------------------------------------------------------- '''
#统计关键词及个数
def CountKey(str1):
    try:
        table = {}
        words = str1.split(" ")
        for word in words:
            if word!="" and table.has_key(word):
                num = table[word]
                table[word] = num + 1
            elif word!="":
                table[word] = 1

        #键值从大到小排序
        dic = sorted(table.iteritems(), key = lambda asd:asd[1], reverse = True)
        return dic
        
    except Exception,e:    
        print 'Error:',e


''' ------------------------------------------------------- '''
def MergeKeys(dic1,dic2):
    #合并关键词
    aryKey = []
    for i in range(len(dic1)):
        aryKey.append(dic1[i][0])
    for i in range(len(dic2)):       
        if dic2[i][0] in aryKey:
            continue
        else:
            aryKey.append(dic2[i][0])
    
    test = str(aryKey).decode('string_escape')

    #计算词频
    aryNum1 = [0]*len(aryKey)
    aryNum2 = [0]*len(aryKey)
    
    #赋值aryNum1
    for i in range(len(dic1)):     
        key = dic1[i][0]
        value = dic1[i][1]
        j = 0
        while j < len(aryKey):
            if key == aryKey[j]:
                aryNum1[j] = value
                break
            else:
                j = j + 1

    #赋值aryNum2
    for i in range(len(dic2)):     
        key = dic2[i][0]
        value = dic2[i][1]
        j = 0
        while j < len(aryKey):
            if key == aryKey[j]:
                aryNum2[j] = value
                break
            else:
                j = j + 1
    

    #计算两个向量的点积
    x = 0
    i = 0
    while i < len(aryKey):
        x = x + aryNum1[i] * aryNum2[i]
        i = i + 1

    #计算两个向量的模
    i = 0
    sq1 = 0
    while i < len(aryKey):
        sq1 = sq1 + aryNum1[i] * aryNum1[i]   #pow(a,2)
        i = i + 1
    
    i = 0
    sq2 = 0
    while i < len(aryKey):
        sq2 = sq2 + aryNum2[i] * aryNum2[i]
        i = i + 1
    try: 
        res = float(x) / ( math.sqrt(sq1) * math.sqrt(sq2) )
    except:
        res=0
    return res
    


def vsm(str1,str2):

    dic1 = CountKey(str1)
    
    dic2 = CountKey(str2)

    res = MergeKeys(dic1, dic2)

    return res

def vsm2(list1,list2):

    dic1 = CountKey1(list1)
    
    dic2 = CountKey1(list2)

    res = MergeKeys(dic1, dic2)

    return res

