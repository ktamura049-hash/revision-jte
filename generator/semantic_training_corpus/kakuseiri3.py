# -*- coding:utf-8 -*-
#kakuseiri3.py

#

import os
import sys
import random
import copy
from kakutaple4 import cdict
from operator import itemgetter

def kakuhenkan(kaku):
    if kaku == 0:
        return 'が'
    if kaku == 1:
        return 'を'
    if kaku == 2:
        return 'に'
    if kaku == 3:
        return 'へ'
    if kaku == 4:
        return 'と'
    if kaku == 5:
        return 'で'
    if kaku == 6:
        return 'から'
    if kaku == 7:
        return 'より'
    if kaku == 8:
        return 'まで'
    if kaku == 9:
        return 'の'
    else:
        return'$'

def k2i(kaku):
    if kaku == 'が':
        return 0
    if kaku == 'を':
        return 1
    if kaku == 'に':
        return 2
    if kaku == 'へ':
        return 3
    if kaku == 'と':
        return 4
    if kaku == 'で':
        return 5
    if kaku == 'から':
        return 6
    if kaku == 'より':
        return 7
    if kaku == 'まで':
        return 8
    if kaku == 'の':
        return 9
    else:
        return 999
    

def kakuhyou(filename):

    verb, name, taple = cdict(filename)
    taples = []
    wordlist = []
    allt = []

    for i in range(0,len(taple)):
        taples.append((taple[i][0],taple[i][1][0]))
        wordlist.append(taple[i][0])
    chars = sorted(list(set(wordlist)))
    taples = sorted(taples)
    seiri = set(taples)
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    for i in range(0,len(chars)):
        for j in range(0,11):
            allt.append((chars[i],j))
    allt = set(allt)

    allhi = allt - seiri
    allhi = sorted(allhi)

    tangoram =''
    tangoram = allhi[0][0]
    hi = []
    listram = []

    for i in range(0,len(allhi)):
        if tangoram == allhi[i][0]:
            pass
        else:
            hi.append(listram)
            listram = []
            tangoram = allhi[i][0]
        listram.append(allhi[i][1])
    hi.append(listram)
    
    #以下正解用の格の集合作成を追加
    seiri = set(allhi)
    allse = allt - seiri
    allse= sorted(allse)
    tangoram =''
    tangoram = allse[0][0]
    sei = []
    listram = []

    for i in range(0,len(allse)):
        if tangoram == allse[i][0]:
            pass
        else:
            sei.append(listram)
            listram = []
            tangoram = allse[i][0]
        listram.append(allse[i][1])
    sei.append(listram)
    #追加おわり

    #print(chars[0],allse[0],allhi[0])
    taple3 = sorted(taple, key = lambda x:x[1][1],reverse = True)
    #for i in range(0,100):
    #print(taple3[i])

    return chars,sei,hi,taple3
    

    

if __name__ == '__main__':

    taple = []
    filename = 'bunresult3.txt'
    chars,taple1,taple2, taple3  = kakuhyou(filename)
    for i in range(100):
        print(chars[i],taple1[i],taple2[i],taple3[i])
    
    print(len(chars),len(taple1),len(taple2))

    
    
        
