#-*- unicode-8 -*-
#bunrui.py

#格フレームのxmlファイルから格の要素を抜き出す＆正例文をつくる

import sys
import os
import re
import copy

#読み込んだ行を", <, >, :で区切る
def syori(line):
    #記号 ", <, >, :タブに変換する
    line = re.sub('\"|<|>|\:','\t',line)
    #行を区切る
    line = line.split()
    return line

'''
格フレーム辞書から動詞と格、最頻の名詞を抽出する関数
bunrui(filename)
filename = 格フレーム辞書を指定する

以下例
----------------
見える 動 999
ガ格 555
あなた 555
カラ格 444
遠く 444
----------------
'''
def bunrui(filename):
    #変数定義
    tangoram = []
    kakuram = []
    lineram = 0
    lineram2 = 0
    head = 0

    #fileを開く
    with open(filename) as f:
        #一行読み込む
        line = f.readline()
        #行がまだあるときつづける
        while line:
            #記号で分割
            line = syori(line)
            #
            if 'caseframe' in line:         
                suru = 0
                print('----------------')
                for i in range(0,len(line)):
                    if '/' in line[i]:
                        lineram = copy.deepcopy(line[i])
                        lineram  = lineram.replace('/','\t').split()
                        if len(lineram) > 1:
                            if '+する' in lineram[1]:
                                lineram[0] = lineram[0] + 'する'
                        line[i] = lineram[0]
                        lineram = i
                        lineram2 = i
                    if 'frequency'in line[i]:
                        lineram3 = i
                print(line[lineram],line[lineram2 + 1],line[lineram3+1])
                head += 1
                
            if 'argument' in line:
                for i in range(0,len(line)):
                    if 'case' in line[i]:
                        lineram = i
                    if 'frequency' in line[i]:
                        lineram2 = i    
                print(line[lineram+1],line[lineram2+1])
                line = f.readline()
                line = syori(line)
                for k in range(0,len(line)):
                    if 'frequency' in line[k]:
                        lineram2 = k
                        break
                i = len(line)-2
                for j in range(0,len(line[i])-1):
                    if line[i][j] == '/':
                        lineram = j
                        break
                    else:
                        lineram = 1
                line[i] = line[i][0:lineram]
                print(line[i], line[lineram2+1])
                
            line = f.readline()

if __name__ == '__main__':

    taple = []
    filename = './kaku.xml'
    bunrui(filename)             
