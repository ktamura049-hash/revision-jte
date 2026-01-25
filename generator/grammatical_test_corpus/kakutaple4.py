# -*- coding:utf-8 -*-
#kakutaple.py

#（単語,格,前の単語）の集りをつくる
import os
import sys
import numpy as np
import math
import random

def cdict(filename):
    kaku = ['ガ格', 'ヲ格','ニ格','ヘ格','ト格','デ格','カラ格','ヨリ格','マデ格','ノ格']

    taple = []
    tangoram = ''
    maeram = ''
    head = 0
    name= []
    for i in range(0,len(kaku)):
        ndict = dict()
        name.append(ndict)
    verb = dict()
    kdict = dict()
    #fileを読み込む
    with open(filename) as f:
        #1行読む
        line = f.readline()
        #fileが続くかぎり
        while line:
            if '----' in line:
                line = f.readline()
                line = line.split()
                if len(line) > 1:
                    if '動' in line[1]:
                        tangoram = line[0]
                        verb[tangoram] = verb.get(tangoram,0) + int(line[2])
                    else:
                        tangoram = line[0] + '*'
                else:
                    tangoram = line[0] + '*'
                #verb[tangoram] = verb.get(tangoram,0) + int(line[2])
                head += 1
                line = f.readline()
            line = line.split()
            if '格' in line[0]:
                status = 0
                for i in range(0,len(kaku)):
                    if line[0] == kaku[i]: 
                        hindoram = line[1]
                        line = f.readline()
                        line = line.split()
                        #print(line[0]) 
                        name[i][line[0]] = name[i].get(line[0],0) + int(line[1])
                        taple.append((tangoram,(i,int(hindoram)),line[0]))
                        status = 1
                    if i == 9:
                        if kaku[9] in line[0]:
                            hindoram = line[1]
                            line = f.readline()
                            line = line.split()
                            name[9][line[0]] = name[9].get(line[0],0) + int(line[1])
                            taple.append((tangoram,(i,int(hindoram)),line[0]))
                            status = 1

                if status == 0:
                    line = f.readline()
                line = f.readline()
            else:
                line = f.readline()
                line = f.readline()

    return verb, name, taple


if __name__ == '__main__':

    taple = []
    kaku = ''
    filename = './bunresult3.txt'
    verb, name, taple= cdict(filename)
    number = 10
    j = 0
    print()
    print('Verb')
    print()
    for v,c in sorted(verb.items(), key=lambda x:x[1], reverse = True):
        print(v)
        j += 1
        if j > 10:
            break
    for i in range(0, 10):
        print()
        print('name'+str(i))
        print()
        j = 0
        for n,c in sorted(name[i].items(), key=lambda x:x[1], reverse = True):
           print(n)
           j += 1
           if j > 10:
               break
    print(taple[0])


'''
    print('----------')
    for i in range(0,len(taple)):
        if taple[i][1] == 0:
            kaku = 'が'
        if taple[i][1] == 1:
            kaku = 'を'
        if taple[i][1] == 2:
            kaku = 'に'
        if taple[i][1] == 3:
            kaku = 'へ'
        if taple[i][1] == 4:
            kaku = 'と'
        if taple[i][1] == 5:
            kaku = 'で'
        if taple[i][1] == 6:
            kaku = 'から'
        if taple[i][1] == 7:
            kaku = 'より'
        if taple[i][1] == 8:
            kaku = 'まで'
        if taple[i][2] == '&':
            pass
        else:
            print(taple[i][2] + kaku + taple[i][0])
            print('----------')
'''             
                
