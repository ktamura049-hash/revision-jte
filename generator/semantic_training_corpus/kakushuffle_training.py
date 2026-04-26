#-*- coding:utf-8 -*-
#kakushuffle2.py

#コーパス内の格助詞をとりうる別の格助詞に変更

from katsuyou import syutoku
from kakuseiri3 import kakuhyou, kakuhenkan, k2i
from cre_sent import save_sentence, remove_file
import random
import copy
import sys,os

#path
#corpus:入力とする正文のコーパス
corpus = sys.argv[1]
corpus_filename = corpus.split('/')[-1]

#h_corpus:出力となる非文コーパス
#t_corpus:非文が出力された正文コーパス
#n_corpus:非文にならないときはNoneと表示する非文コーパス
h_corpus = 'hibun_corpus/imihibun'+corpus_filename
t_corpus = 'seibun_corpus/'+corpus_filename
n_corpus = 'hibun_corpus/none_'+corpus_filename

remove_file(h_corpus)
remove_file(t_corpus)
remove_file(n_corpus)


with open(corpus, 'r') as f:
    lines = f.read()
    lines = lines.replace('<eos>\n','<eos>').replace('<eos>','\n').replace(' ','').split('\n')
    

for i in range(10):
    print(lines[i])


#動詞、正しい格助詞、間違った格助詞の取得
#filename：格フレームコーパス
dir = os.path.join(os.environ["EXPERIMENT_PATH"],"generator")
filename = os.path.join(dir,'bunresult.txt')
#chars：単語のリスト、sei：正しい格助詞のリスト、hi:間違った格助詞のリスト
chars, sei, hi, taple = kakuhyou(filename)
#c2i：単語を単語IDに変換。char2index、　i2c：単語IDを単語に変換。index2chars
c2i = dict((c,i) for i,c in enumerate(chars))
i2c = dict((i,c) for i,c in enumerate(chars))
for ram in [0, 100, -1]:
    print(chars[ram],i2c[c2i[chars[ram]]])
    print(sei[c2i[chars[ram]]],sei[ram])
    print(hi[c2i[chars[ram]]],hi[ram])

#チェック
print(chars[c2i['重なる']])


#各文ごとに処理する
for ram in range(len(lines)):
    print('-'*50)
    #mecabによる形態素解析を行い、正文の各単語を得る
    taple = syutoku(lines[ram])
    hi_num = []
    hi_case = []
    #遡り始める位置
    start = 0
    #文の単語をひとつひとつ見ていく
    for i in range(len(taple)):
        #print(taple[i])
        #MeCabの結果格助詞とされたとき
        if taple[i][1] == '動詞':
            #taple[i][3]：単語の原形
            print(taple[i][3])
            if taple[i][3] in chars:
                #文を遡って格助詞を見つけて、格助詞を変更
                for j in range(start, i):
                    if taple[j][2] == '格助詞' and taple[j][4] == '一般':
                        #その動詞の正しい格と間違った格助詞のリストを取得
                        vs = copy.deepcopy(sei[c2i[taple[i][3]]])
                        vhi = copy.deepcopy(hi[c2i[taple[i][3]]])
                        print('正の格助詞：',vs,'\t負の格助詞：', vhi)
                        #格助詞をidに変更
                        vs_id = k2i(taple[j][0])
                        if vs_id == 999:
                            continue
                        #取りうる格助詞が1つしかない場合を回避
                        #擁す
                        #正の格助詞： [1]        負の格助詞： [0, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                        if len(vs) == 1:
                            continue
                        #取りうる格助詞のリストから格助詞を削除
                        try:
                            vs.remove(vs_id)
                            print('正の格助詞：',vs)
                        except:
                            print('格助詞の削除に失敗')
                            continue
                        #その位置を記録
                        hi_num.append(j)
                        #取りうる格助詞の中からランダムに取得
                        sel_vs = random.choice(vs)
                        hi_case.append(kakuhenkan(sel_vs))
                    start = i
        
            

    if len(hi_num) != len(hi_case):
        continue
    
    #変更できる格助詞が存在した場合
    if len(hi_num) != 0:
        count = 0
        print(hi_num)
        print(hi_case)

        w_hisens = []
        for ramnum in range(len(hi_num)):
            seisen = '' #正文の変数
            hisen = ''  #非文の変数(表示用)
            w_hisen = ''  #非文の変数（書込み用）
            for i in range(len(taple)):
                seisen = seisen+taple[i][0]+' '
                if i == hi_num[ramnum]:
                    hisen = hisen+'＜'+hi_case[ramnum]+'＞'
                    w_hisen = w_hisen+'$'+hi_case[ramnum]+' '
                else:
                    hisen = hisen + taple[i][0]
                    w_hisen =  w_hisen + taple[i][0]+' '
            print('正文：',seisen)
            print('非文：',hisen)
            w_hisens.append(w_hisen)
        c_hisens = ''
        for i in range(len(w_hisens)):
            c_hisens = c_hisens + w_hisens[i] + '\t'
        save_sentence(t_corpus, seisen)
        save_sentence(h_corpus, c_hisens)
        save_sentence(n_corpus, c_hisens)
        
        
    #変更しようがない場合は変更なしと表示
    else:
        print('変更なし')
        save_sentence(n_corpus, 'None')


                                
