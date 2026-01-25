#-*- coding:utf-8 -*-
#cresent.py

#単文を作成するための関数

from kakutaple4 import cdict
from kakuseiri3 import kakuhyou, kakuhenkan
from katsuyou import syutoku, te, setsuzoku, marge_heiritsu
import sys
import os
import random
import copy
import io
import csv

#名詞を<unk>に変更
def unk():
    name = ''
    name = '<unk>'
    return name

#nnumをnamelen進に
def nlen_shin(length, nnum, namelen):
    nc = []
    #空のリストを設定nc = [0][0][0][0]...となるはず
    for k in range(length):
        nc.append(0)
    #現在の生成回数をnamelenで割るとその都度の余りで
    #namelen進数が作られる
    for k in range(1,length+1):
        nc[-k] = nnum % namelen
        nnum = int(nnum) / namelen
    return nc

#名詞と格助詞をつなげる
def connect(sentence, *words):
    for word in words:
        #print(word, type(word))
        if type(word) is list :
            for i in range(len(word)):
                if word[i] == '<eos>' or word[i] == '\n':
                    sentence = sentence + str(word[i])
                else:
                    sentence = sentence+str(word[i])+' '
        else:
            if word == '<eos>' or word == '\n':
                sentence = sentence + str(word)
            else:
                sentence = sentence+str(word)+' '
    return sentence

#名詞＋格助詞の状態を作る
#vs:正文の格助詞、vhi:非文の格助詞、length:長さ
#namelen:名詞の種類 names:名詞の格納先 hinum:非文にする格助詞の位置
def tanbun(vss, vhis,length, namelen, names, hinum, unk_mode=0):
    sentence = ''
    hisen = ''
    #各格助詞で名詞の数（namelen）だけ文を生成する
    #namelen進数の列を作ることで管理する
    #まずは総数を計算namelenのlength乗
    num = namelen
    for j in range(length - 1):
        num = num * namelen
    #総数分の文と非文のペアを作成
    for j in range(num):
        #nlen_shinを使ってnamelen進に
        nc = nlen_shin(length, j, namelen)
        #名詞＋格助詞を文に加える
        for k in range(length):
            name = ''
            if unk_mode == 1:
                name = unk()
            else:
                name = names[vss[k]][int(nc[k])]
            sentence = connect(sentence, name, kakuhenkan(vss[k]))
            hisen = connect(hisen, name)
            #非文の方は、格を変更させる位置になったら
            #非文の格を正しい格と入れ替える
            if k == hinum:
                hisen = connect(hisen, (kakuhenkan(vhis)))
            else:
                hisen = connect(hisen, (kakuhenkan(vss[k])))
    return sentence, hisen

#ファイルに文を追加する
def save_sentence(filename, sentence, mode = 'a'):
    with open(filename, mode) as f:
        f.write(sentence + '\n')
    print('save file: ', filename)
    return


# csvで保存
def save_sentence_csv(path, sentence):
    with io.open(path, "a") as f:
        writer = csv.writer(f)
        writer.writerow(sentence)
    return

#プログラムの再開時等に、前のプログラムで作成したファイルを削除する
def remove_file(filename):
    #filenameが存在する時に消す
    if os.path.exists(filename):
        os.remove(filename)

#ファイルをの名付け
def file_naming(filename, length, hinum, vc, namelen,unk_mode=0, bikou = None):
    if bikou != None:
        filename = filename+'_'+bikou+'_'
    if unk_mode == 1:
        filename=filename+'l'+str(length)+'h'+str(hinum)+'v'+str(vc)+'_unk'
    else:
        filename=filename+'l'+str(length)+'n'+str(namelen)+'h'+str(hinum)+'v'+str(vc)
    filename= filename+'.txt'
    
    return filename

#ファイルを一行ずつリストにして読み込む(文を作成する動詞、名詞で使用)
def data_read(filename):
    with open(filename) as f:
        lists = []
        line = f.readline()
        while line:
            line = line[:-1]
            if line in lists:
                pass
            else:
                lists.append(line)
            line = f.readline()
    return lists

