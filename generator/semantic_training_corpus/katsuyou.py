#-*- coding:utf-8 -*-
#katsuyou.py

#動詞を活用させる

from kakutaple4 import cdict
from kakuseiri3 import kakuhyou, kakuhenkan
#from sudachipy import tokenizer, dictionary
import sys
import os
import random
import copy
import io
import MeCab

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


def syutoku(text):
    m = MeCab.Tagger("")
    m.parse('')

    taple = []

    node = m.parseToNode(text)
    while node:
        #単語を取得
        word = node.surface
        #単語以下の情報を取得
        nodes = node.feature.split(',')
        #品詞を取得
        hinsi = nodes[0]
        #品詞の細かい分類
        bun = nodes[1]
        #活用法（五段活用など）
        kei = nodes[4]
        #原形
        gen = nodes[6]
        #格助詞の連語、一般
        kakubun = nodes[2]
        
        if hinsi != 'BOS/EOS':
            taple.append((word,hinsi, bun, gen, kakubun, kei))
        #print(nodes)
        '''
        for i in range(len(nodes)):
            pos = nodes[i]
            print(word)
            print(pos, i)
        '''
        #print(node.feature)
        #次の単語に進める
        node = node.next
        
    return taple

def te(taple):
    hatsuon = ['む','ぶ','ぬ']
    sokuon = ['う','ふ','つ','る']
    henka = taple[0]
    if taple[-1] == 'サ変・スル':
        henka = 'し て'
    if taple[-1] == 'カ変・来ル':
        henka = '来 て'
    #上一段活用のときは最後の1文字を消して、てをつける
    #出る→出て
    if '一段' in taple[-1]:
        henka = henka[:-1]+' て'
    #mecab自体に「五段活用促音便」等と
    #戦う→戦って
    elif '促音便' in taple[-1]:
        henka = henka[:-1]+'っ て'
    elif '撥音便' in taple[-1]:
        henka = henka[:-1]+'ん で'
    elif 'イ音便' in taple[-1]:
        henka = henka[:-1]+'い て'
    elif '五段' in taple[-1]:
        if 'カ行' in taple[-1]:
            henka = henka[:-1]+'い て'
        elif 'ガ行' in taple[-1]:
            henka = henka[:-1]+'い で'
        elif 'サ行' in taple[-1]:
            henka = henka[:-1]+'し て'
        elif henka[-1] in hatsuon:
            henka = henka[:-1]+'ん で'
        elif henka[-1] in sokuon:
            henka = henka[:-1]+'っ て'
        else :
            henka = henka[:-1]+' て'
    else :
            henka = henka[:-1]+' て'

    kaeri = (henka, taple[1], taple[2])
    return kaeri

def ta(taple):
    hatsuon = ['む','ぶ','ぬ']
    sokuon = ['う','ふ','つ','る']
    henka = taple[0]
    if taple[-1] == 'サ変・スル':
        henka = 'し た'
    if taple[-1] == 'カ変・来ル':
        henka = '来 た'
    if '一段' in taple[-1]:
        henka = henka[:-1]+' た'
    elif '促音便' in taple[-1]:
        henka = henka[:-1]+'っ た'
    elif '撥音便' in taple[-1]:
        henka = henka[:-1]+'ん だ'
    elif 'イ音便' in taple[-1]:
        henka = henka[:-1]+'い た'
    elif '五段' in taple[-1]:
        if 'カ行' in taple[-1]:
            henka = henka[:-1]+'い た'
        elif 'ガ行' in taple[-1]:
            henka = henka[:-1]+'い だ'
        elif 'サ行' in taple[-1]:
            henka = henka[:-1]+'し た'
        elif henka[-1] in hatsuon:
            henka = henka[:-1]+'ん だ'
        elif henka[-1] in sokuon:
            henka = henka[:-1]+'っ た'
        else :
            henka = henka[:-1]+' た'
    else :
        henka = henka[:-1]+' た'

    kaeri = (henka, taple[1], taple[2])
    return kaeri

def setsuzoku(text, mode, unk = 0):
    taple = syutoku(text)
    #print(unk)
    '''
    for i in range(len(taple)):
        print(taple[i])
    '''
    sentence = ''
    count = 0
    for i in range(len(taple)):
        if taple[i][1] == '動詞':
            count += 1
            if count == 1:
                #print(taple[i])
                if mode == te:
                    taple[i] = te(taple[i])
                if mode == ta:
                    taple[i] = ta(taple[i])
        #print(taple[i])
        sentence = sentence+taple[i][0]
    #print('-'*40)
    taple = syutoku(sentence)
    #print(taple)
    kakujoshi = ['が','を','に','へ','と','で','から','まで','より','の']
    if unk == 1:
        #print('success')
        for i in range(len(taple)):
            #print(taple[i-1])
            #MeCabが格助詞を判断してくれない時があるので中止
            #if taple[i][2] == '格助詞' :
            for j in kakujoshi:
                if taple[i][0] == j:
                    taple[i-1] = ('<unk>', taple[i-1][1], taple[i-1][2], taple[i-1][3])
    sentence = ''
    for i in range(len(taple)):
        sentence = sentence+taple[i][0]+' '
    sentence = sentence + '<eos>'
    return sentence

def marge_heiritsu(text1, text2, unk = 0):
    #sentence = text1+' 、 '+text2+' 。'
    #print(unk)
    #print (sentence)
    #sentence = setsuzoku(sentence, te, unk)
    sentence = ''
    sentence = connect(sentence, text1, '、', text2, '。','<eos>')
    return sentence

#text1 = 非修飾文、text2 = 連体節
def marge_rentai(text1, text2, syusyoku, touten = 0):
    #sentence = text1+' '+text2+' 。'
    #print(unk)
    #print(sentence)
    #sentence = setsuzoku(sentence, ta, unk)
    #入力文をそれぞれリスト化
    texts1 = text1.split()
    texts2 = text2.split()
    sentence = ''
    #修飾する位置が０じゃないときは最初にそれまでの単語をくっつけておく
    if syusyoku != 0:
        sentence = connect(sentence, texts1[:2*syusyoku])
        if touten == 1:
            sentence = connect(sentence, '、')
    #連体節
    sentence = connect(sentence, texts2)
    #非修飾
    sentence = connect(sentence, texts1[2*syusyoku:], '。', '<eos>')
    return sentence


#補足節の複文を作成する関数
#text1=主節, text2=従属節,　syusyoku=修飾位置，kaku=変更する格助詞
def marge_noun(text1, text2, syusyoku, kaku, touten = 0):
    print(type(text1))
    #入力文をそれぞれリスト化
    if 'list' in str(type(text1)):
        texts1 = copy.deepcopy(text1)
    else:
        texts1 = text1.split()
    if 'list' in str(type(text2)):
        texts2 = copy.deepcopy(text2)
    else:
        texts2 = text2.split()
        
    sentence = ''
    #修飾する位置が０じゃないときは最初にそれまでの単語をくっつけておく
    if syusyoku != 0:
        sentence = connect(sentence, texts1[:2*syusyoku])
        if touten == 1:
            sentence = connect(sentence, '、')
    #名詞節
    sentence = connect(sentence, texts2)
    if kaku != None:
        sentence = connect(sentence, 'こと', kakuhenkan(kaku))
    else:
        sentence = connect(sentence, 'こと')
    #非修飾
    sentence = connect(sentence, texts1[2*syusyoku:], '。', '<eos>')
    return sentence
    

if __name__ == '__main__':
    text1 = '弟 が ゲーム で 遊ぶ'
    text2 = '学校 まで 向う'
    syusyoku = 1
    kaku = random.randrange(10)
    #text = sys.argv[1]
    #print('-'*40)
    print('主節：',text1, '\t従属節',text2)
    print()
    sentence1 = marge_heiritsu(text1,text2, 1)
    sentence2 = marge_rentai(text1,text2, syusyoku)
    sentence3 = marge_noun(text1,text2, 1, kaku)
    #print('並立節の複文： ', sentence1)
    print('連体節の複文： ', sentence2)
    #print('名詞節の複文： ', sentence3)
    sentence2 = marge_rentai(text1,text2, syusyoku,touten = 1)
    print('連体節の複文： ', sentence2)
    print()
    
    '''
    for i in range(10):
        sentence3 = marge_noun(text1,text2, 1, i)
        print('名詞節の複文',i,'：', sentence3)
    '''
