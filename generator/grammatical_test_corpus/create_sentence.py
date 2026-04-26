#-*- coding:utf-8 -*-
# create_sentence.py

#コーパスの作成

from kakutaple4 import cdict
from kakuseiri3 import kakuhyou, kakuhenkan
from katsuyou import *
from cre_sent import *
import sys
import os
import random
import copy
import io
import itertools
import argparse

def main(args):
    dir = os.path.join(os.environ["EXPERIMENT_PATH"],"generator")
    filename = os.path.join(dir,'bunresult.txt')
    with open('./verb.txt') as f:
        #verbs = [s.strip() for s in f.readlines()]
        verbs = []
        line = f.readline()
        while line:
            line = line[:-1]
            if line in verbs:
                pass
            else:
                verbs.append(line)
            line = f.readline()
    names = []
    for i in range(0,10):
        with open('./name'+str(i)+'.txt') as f:
            name = [s.strip() for s in f.readlines()]
        names.append(name)
    chars, sei, hi, taple = kakuhyou(filename)
    c2i = dict((c,i) for i,c in enumerate(chars))
    i2c = dict((i,c) for i,c in enumerate(chars))
            

    if args.mode == 'simple' or args.mode == 'all':
        create_simple(args.pair, args.noun, args.hinum, args.start_verb, args.vc, verbs, names, sei, hi, c2i, args.unk)
    if args.mode == 'adv' or args.mode == 'all':
        create_complex_adv(args.pair, args.noun, args.hinum, args.start_verb, args.vc, verbs, names, sei, hi, c2i, args.unk, args.touten)
    if args.mode == 'adj' or args.mode == 'all':
        create_complex_adj(args.pair, args.noun, args.hinum, args.start_verb, args.vc, verbs, names, sei, hi, c2i, args.unk, args.touten)
    if args.mode == 'sup' or args.mode == 'all':
        create_complex_sup(args.pair, args.noun, args.hinum, args.start_verb, args.vc, verbs, names, sei, hi, c2i, args.unk, args.touten)

# 単文を作成する
def create_simple(length, namelen, hinum, start_verb, vc, verbs, names, sei, hi, c2i, unk):
    counter = 0

    #fileに名前をつける
    #書き込みファイルの名前
    write_file = file_naming('simple_', length, hinum, vc, namelen, unk)
    #ファイルが既存なら前のを消す
    remove_file(write_file)
    
    for i in range(start_verb,len(verbs)):
        sentence = ''
        hisen = ''
        vs = copy.deepcopy(sei[c2i[verbs[i]]])
        vhi = copy.deepcopy(hi[c2i[verbs[i]]])
        del vhi[-1]
        if len(vs) > length - 1 and len(vs) < 10:
            en = 1
            while en:
                vss = random.sample(vs,length)
                if vss[-1] == 9:
                    pass
                else:
                    en = 0
            for pvs in itertools.permutations(vss):
                vhis = random.choice(vhi)

                sentence, hisen = tanbun(pvs, vhis, length, namelen, names, hinum, unk)
                sentence = connect(sentence, verbs[i], '。', '<eos>')
                hisen = connect(hisen, verbs[i], '。', '<eos>')
                print(sentence)
                print(hisen)
                save_sentence(write_file, sentence)
                save_sentence(write_file, hisen)
            counter += 1
            if counter == vc:
                return
            else:
                print('-' * 50)

# 連用節
def create_complex_adv(length, namelen, hinum, start_count, vc, verbs, names, sei, hi, c2i, unk, touten):
    #接続する単語のリストをファイルから読み込む
    hei_list = data_read('./hei_list.txt')
    print('hei_list: ',hei_list )
    te_list = data_read('./te_list.txt')
    print('te_list: ',te_list )
    jou_list = data_read('./jou_list.txt')
    print('jou_list: ',jou_list )
    ri_list = data_read('./ri_list.txt')
    print('ri_list: ',ri_list )
    time_list = data_read('./time_list.txt')
    print('time_list: ',time_list )
    ta_list = data_read('./ta_list.txt')
    print('ta_list: ',ta_list )
    
    setu_list = [hei_list, te_list, jou_list, ri_list, time_list]
    #主節になる文を格納する
    main_sentences = []
    main_hisens = []
    #従属節になる文＋接続を格納する。節ごとに分ける
    sub_sentences = []
    sub_hisens = []
    for ram in setu_list:
        sub_sentences.append([])
        sub_hisens.append([])

    #fileに名前をつける
    #書き込みファイルの名前
    write_file = file_naming('complex_adv', length, hinum, vc, namelen, unk, bikou='sub')
    write_file2 = file_naming('complex_adv', length, hinum, vc, namelen, unk, bikou='main')
    #ファイルが既存なら前のを消す
    remove_file(write_file)
    remove_file(write_file2)

    counter = 0
    taple = []
    
    #各動詞ごとの挙動
    for i in range(start_count,len(verbs)):
        sentence = ''
        hisen = ''
        #動詞の正しい格助詞と非文用の格助詞を読み込む
        vs = copy.deepcopy(sei[c2i[verbs[i]]])
        vhi = copy.deepcopy(hi[c2i[verbs[i]]])
        print(verbs[i],vs, vhi)
        if len(vs) > length - 1 and  len(vs) < 10:
            en = 1
            while en :
                #正しい格助詞からランダムに選択
                main_vss = random.sample(vs,length)
                sub_vss = random.sample(vs, length)
                #～の＜動詞＞で文が終わると変なので、最後が「の」になったらループ
                if main_vss[-1] == 9  or sub_vss[-1] == 9:
                    pass
                else:
                    en = 0
        else:
            print('skip:', verbs[i])
            continue
        #ランダムに非文とする格を選択
        del vhi[-1]
        vhis = random.choice(vhi)
        #主節の文の作成
        sentence, hisen = tanbun(main_vss, vhis, length, namelen, names, hinum, unk)
        main_sentence = connect(sentence,verbs[i])
        main_hisen = connect(hisen,verbs[i])
        #主節の文の追加
        main_sentences.append(main_sentence)
        main_hisens.append(main_hisen)
        
        #従属節の文の作成
        sentence = ''
        hisen = ''
        sentence, hisen = tanbun(sub_vss, vhis, length, namelen, names, hinum, unk)
        
        for j in range(len(setu_list)):
            syurui = random.choice(setu_list[j])
            
            #て節と時間節「以来」のとき連用形＋テの形にする
            if syurui in te_list or syurui == '以来':
                taple = syutoku(verbs[i])
                print(verbs[i],taple)
                taple[-1] = te(taple[-1])
                te_verbs = []
                for ram in taple:
                    te_verbs.append(ram[0])
                sub_sentence = connect(sentence, te_verbs)
                sub_hisen = connect(hisen, te_verbs)
                #てじゃないときは追加
                if syurui != 'て':
                    #以来じゃないときは分離した次の単語を追加
                    if syurui != '以来':
                        syurui = syurui.split()
                        syurui = syurui[1]
                    sub_sentence = connect(sub_sentence, syurui)
                    sub_hisen = connect(sub_hisen, syurui)
                    
            #連用形＋タ形にするとき連用形＋タ形にする。
            elif syurui in ta_list:
                taple = syutoku(verbs[i])
                print(verbs[i],taple)
                taple[-1] = ta(taple[-1])
                ta_verbs = []
                for ram in taple:
                    ta_verbs.append(ram[0])
                if syurui == 'たり' or syurui == 'たら':
                    #うしろの一文字を追加
                    ta_verbs.append(syurui[1])
                    sub_sentence = connect(sentence, ta_verbs)
                    sub_hisen = connect(hisen, ta_verbs)
                else:
                    sub_sentence = connect(sentence, ta_verbs, syurui)
                    sub_hisen = connect(hisen, ta_verbs, syurui)

            #そうでないときは原形に直接つなげる
            else:
                sub_sentence = connect(sentence, verbs[i], syurui)
                sub_hisen = connect(hisen, verbs[i], syurui)
            #従属節の文の追加
            print(sub_sentence, sub_hisen)
            sub_sentences[j].append(sub_sentence)
            sub_hisens[j].append(sub_hisen)
            
        #条件をクリアする動詞をあつめてるためbreak等で抜けるのがこわいので↓
        #動詞の数vcだけ繰り返したら生成ぷろぐらむへ
        counter += 1
        if counter == vc:
            sentence = ''
            hisen = ''
            #文と文数のチェック
            for ram in range(len(main_sentences)):
                print('正文',main_sentences[ram],'\t非文', main_hisens[ram])
            print(len(main_sentences),len(main_hisens))
            for ram in range(len(sub_sentences)):
                print(len(sub_sentences[ram]), len(sub_hisens[ram]))
            #rama =前の文、 ramb = 後の文
            for ram in range(len(sub_sentences)):
                for rama in range(len(sub_sentences[ram])):
                    for ramb in range(len(main_sentences)):
                        #同じ文の時はパス
                        if rama == ramb:
                            #print('same')
                            pass
                        else:
                            #主節のペア
                            #主節のペア
                            sentence = marge_heiritsu2(main_sentences[ramb], sub_sentences[ram][rama], unk, touten)
                            hisen = marge_heiritsu2(main_hisens[ramb], sub_sentences[ram][rama], unk, touten)
                            print(sentence)
                            print(hisen)
                            save_sentence(write_file2, sentence)
                            save_sentence(write_file2, hisen)
                            
                            #従属節のペア
                            sentence = marge_heiritsu2(main_sentences[ramb], sub_sentences[ram][rama], unk, touten)
                            hisen = marge_heiritsu2(main_sentences[ramb], sub_hisens[ram][rama], unk, touten)
                            print(sentence)
                            print(hisen)
                            save_sentence(write_file, sentence)
                            save_sentence(write_file, hisen)

            #強制終了
            return

# 連体節
def create_complex_adj(length, namelen, hinum, start_count, vc, verbs, names, sei, hi, c2i, unk, touten):
    taple = []
    #従属節が主節のどの名詞を修飾するかを決めるための変数
    #現状０固定
    syusyoku = 0
    
    #修飾する名詞の位置をファイル名に書き込む
    #bikou = 'syusyoku_'+str(syusyoku)
    
    #どこから始めるか
    start_count = 0
    #作成する節境界の種類
    #無標のリスト（一つだけどリスト形式にしたほうが後々楽）
    mu_list = ['mu']
    yuu_list = data_read('./yuu_list.txt')
    print('yuu_list: ',yuu_list )
    '''
    #有標のリスト
    yuu_list = ['あと の', 'かぎり の','ため の','だけ の','て から の','て の','とき の','と の','など の','場合 の','程 の','前 の','まで の','よう な']
    '''
    setsu_list = [mu_list, yuu_list]

    #従属節を格納する
    sub_sentences = []
    sub_hisens = []
    #主節を格納する
    main_sentences = []
    main_hisens = []
    for ram in setsu_list:
        sub_sentences.append([])
        sub_hisens.append([])

    #書き込みファイルの名前
    
    write_file = file_naming('complex_adj', length, hinum, vc, namelen, unk, bikou = 'main')
    write_file2 = file_naming('complex_adj', length, hinum, vc, namelen, unk, bikou = 'sub')
    #write_file3 = file_naming('complex_adj', length, hinum, vc, namelen, unk, bikou = 'touten_main')
    #write_file4 = file_naming('complex_adj', length, hinum, vc, namelen, unk, bikou = 'touten_sub')
    #ファイルが既存なら前のを消す
    remove_file(write_file)
    remove_file(write_file2)
    #remove_file(write_file3)
    #remove_file(write_file4)

    counter = 0
    #各動詞ごとの挙動
    for i in range(start_count,len(verbs)):
        sentence = ''
        hisen = ''
        #動詞の正しい格助詞と非文用の格助詞を読み込む
        vs = copy.deepcopy(sei[c2i[verbs[i]]])
        vhi = copy.deepcopy(hi[c2i[verbs[i]]])
        #つなげる格助詞の数<正しい格助詞の総数<全てのとき
        if len(vs) > length and len(vs) < 10:
            en = 1
            while en :
                #正しい格助詞からランダムに選択
                sub_vss = random.sample(vs,length)
                main_vss = random.sample(vs, length)
                #～の＜動詞＞で文が終わると変なので、最後が「の」になったらループ
                if sub_vss[-1] == 9 or main_vss[-1] == 9:
                    pass
                else:
                    en = 0
        else:
            print('skip:', verbs[i])
            continue
        #ランダムに非文とする格を選択
        del vhi[-1]
        vhis = random.choice(vhi)
        sentence = ''
        hisen = ''
        main_sentence = ''
        main_hisen = ''
        sentence, hisen = tanbun(sub_vss, vhis, length, namelen, names, hinum, unk)
        main_sentence, main_hisen = tanbun(main_vss, vhis, length, namelen, names, hinum, unk)
        main_sentence = connect(main_sentence, verbs[i])
        main_hisen = connect(main_hisen, verbs[i])
        main_sentences.append(main_sentence)
        main_hisens.append(main_hisen)
        for j in range(len(setsu_list)):
            syurui = random.choice(setsu_list[j])
            #連用形＋テ形に変更
            if syurui == 'て から の' or syurui == "て の":
                taple = syutoku(verbs[i])
                print(verbs[i],taple)
                taple[-1] = te(taple[-1])
                te_verbs = []
                for ram in taple:
                    te_verbs.append(ram[0])
                syurui = syurui.split()
                syurui = syurui[1:]
                ram_sentence = connect(sentence, te_verbs, syurui)
                ram_hisen = connect(hisen, te_verbs, syurui)
            #連用形＋タ形に変更
            elif syurui == 'あと の':
                taple = syutoku(verbs[i])
                print(verbs[i],taple)
                taple[-1] = ta(taple[-1])
                ta_verbs = []
                for ram in taple:
                    ta_verbs.append(ram[0])
                ram_sentence = connect(sentence, ta_verbs, syurui)
                ram_hisen = connect(hisen, ta_verbs, syurui)
            elif syurui == 'mu':
                ram_sentence = connect(sentence, verbs[i])
                ram_hisen = connect(hisen, verbs[i])
            else:
                ram_sentence = connect(sentence, verbs[i], syurui)
                ram_hisen = connect(hisen, verbs[i], syurui)
            print(ram_sentence, ram_hisen)
            sub_sentences[j].append(ram_sentence)
            sub_hisens[j].append(ram_hisen)
            
        #条件をクリアする動詞をあつめてるためbreak等で抜けるのがこわいので↓
        #動詞の数vcだけ繰り返したら生成ぷろぐらむへ
        counter += 1
        if counter == vc:
            sentence = ''
            hisen = ''
            #文と文数のチェック
            print('-'*50)
            print('従属節')
            for rama in range(len(sub_sentences)):
                for ram in range(len(sub_sentences[rama])):
                    print('正文',sub_sentences[rama][ram],'\t非文',sub_hisens[rama][ram])
            print('-'*50)
            print('主節')
            for ram in range(len(main_sentences)):
                print('正文',main_sentences[ram],'\t非文',main_hisens[ram])
                print()

            print(len(main_sentences), len(main_hisens))
            #rama =前の文、 ramb = 後の文
            for ram in range(len(sub_sentences)):
                for rama in range(len(sub_sentences[ram])):
                    for ramb in range(len(main_sentences)):
                        #同じ文の時はパス
                        if rama == ramb:
                            #print('same')
                            continue
                        else:
                            print('-'*50)
                            print('主節：', main_sentences[ramb],'\t従属節：',sub_sentences[ram][rama])
                            print()
                            print('従属節の非文のペア') 
                            sentence = (marge_rentai(main_sentences[ramb], sub_sentences[ram][rama], syusyoku,touten))
                            hisen = (marge_rentai(main_sentences[ramb], sub_hisens[ram][rama], syusyoku, touten))
                            print(sentence)
                            print(hisen)
                            save_sentence(write_file2, sentence)
                            save_sentence(write_file2, hisen)
                            #sentence = (marge_rentai(main_sentences[ramb], sub_sentences[ram][rama], syusyoku,touten = 1))
                            #hisen = (marge_rentai(main_sentences[ramb], sub_hisens[ram][rama], syusyoku, touten = 1))
                            #print(sentence)
                            #print(hisen)
                            #save_sentence(write_file4, sentence)
                            #save_sentence(write_file4, hisen)
                            print()
                            print('主節の非文のペア')


                            sentence = ''
                            hisen = ''
                            sentence= (marge_rentai(main_sentences[ramb], sub_sentences[ram][rama], syusyoku, touten))
                            hisen = (marge_rentai(main_hisens[ramb], sub_sentences[ram][rama], syusyoku, touten))
                            print(sentence)
                            print(hisen)
                            save_sentence(write_file, sentence)
                            save_sentence(write_file, hisen)
                            #sentence = (marge_rentai(main_sentences[ramb], sub_sentences[ram][rama], syusyoku, touten = 1))
                            #hisen = (marge_rentai(main_hisens[ramb], sub_sentences[ram][rama], syusyoku, touten = 1))
                            #print(sentence)
                            #print(hisen)
                            #save_sentence(write_file3, sentence)
                            #save_sentence(write_file3, hisen)
                            
                            
            #強制終了
            return


def create_complex_sup(length, namelen, hinum, start_count, vc, verbs, names, sei, hi, c2i, unk, touten):
    # 主節の文を格納する
    main_sentences = []
    main_hisens = []
    # 従属節＋接続を格納する。節ごとに分ける
    sub_sentences = []
    sub_hisens = []
    
    #書き込みファイルの名前
    #主節の格助詞を非文にした正文と非文のペア
    write_file = file_naming('complex_sup', length, hinum, vc, namelen, unk, bikou = 'main')
    #従属節の格助詞を非文にした正文と非文のペア
    write_file2 = file_naming('complex_sup', length, hinum, vc, namelen, unk, bikou = 'sub')
    #ファイルが既存なら前のを消す
    remove_file(write_file)
    remove_file(write_file2)

    # 修飾する名詞の指定 現状0固定
    syusyoku = 0

    
    counter = 0
    #各動詞ごとの挙動
    for i in range(start_count,len(verbs)):
        sentence = ''
        hisen = ''
        #動詞の正しい格助詞と非文用の格助詞を読み込む
        vs = copy.deepcopy(sei[c2i[verbs[i]]])
        vhi = copy.deepcopy(hi[c2i[verbs[i]]])
        print(verbs[i],vs, vhi)
        #つなげる格助詞の数<正しい格助詞の総数<全てのとき
        if len(vs) > length - 1 and len(vs) < 10:
            en = 1
            while en :
                #正しい格助詞からランダムに選択
                sub_vss = random.sample(vs,length)
                main_vss = random.sample(vs,length)
                #～の＜動詞＞で文が終わると変なので、最後が「の」になったらループ
                if sub_vss[-1] == 9  or main_vss[-1] == 9:
                    pass
                else:
                    en = 0
        else:
            print('skip:', verbs[i])
            continue
        #ランダムに非文とする格を選択
        del vhi[-1]
        vhis = random.choice(vhi)
        
        sentence, hisen = tanbun(main_vss, vhis, length, namelen, names, hinum, unk)
        sentence = sentence+verbs[i]
        hisen = hisen+verbs[i]
        main_sentences.append(sentence)
        main_hisens.append(hisen)
        sentence = ''
        hisen = ''

        
        #従属節
        sentence, hisen = tanbun(sub_vss, vhis, length, namelen, names, hinum, unk)
        sentence = sentence+verbs[i]
        hisen = hisen+verbs[i]
        sub_sentences.append(sentence)
        sub_hisens.append(hisen)
        sentence = ''
        hisen = ''
        #条件をクリアする動詞をあつめてるためbreak等で抜けるのがこわいので↓
        #動詞の数vcだけ繰り返したら生成ぷろぐらむへ
        counter += 1
        if counter == vc:
            sentence = ''
            hisen = ''
            #文と文数のチェック
            for ram in range(len(main_sentences)):
                print('正文',main_sentences[ram],'\t非文',main_hisens[ram])
            print(len(main_sentences), len(main_hisens))
            #rama =主節、 ramb = 補足節
            for rama in range(len(main_sentences)):
                for ramb in range(len(sub_sentences)):
                    #同じ文の時はパス
                    if rama == ramb:
                        #print('same')
                        continue
                    else:
                        print('-'*50)
                        print('主節：', main_sentences[rama],'\t従属節：',sub_sentences[ramb])
                        #名詞節につける格助詞の選択
                        #名詞節の最後の単語（動詞）を読み込む
                        s_split = main_sentences[rama].split()
                        h_split = main_hisens[rama].split()
                        
                        #名詞を削除
                        del s_split[2*syusyoku]
                        del h_split[2*syusyoku]
                        
                        #ペアの作成
                        print()
                        print('主節の非文のペア')
                        sentence = (marge_noun(s_split, sub_sentences[ramb], syusyoku, touten))
                        hisen = (marge_noun(h_split, sub_sentences[ramb], syusyoku, touten))
                        print(sentence)
                        print(hisen)
                        save_sentence(write_file, sentence)
                        save_sentence(write_file, hisen)
                        
                        print()
                        print('従属節の非文のペア')
                        sentence = (marge_noun(s_split, sub_sentences[ramb], syusyoku, touten))
                        hisen = (marge_noun(s_split, sub_hisens[ramb], syusyoku, touten))
                        print(sentence)
                        print(hisen)
                        save_sentence(write_file2, sentence)
                        save_sentence(write_file2, hisen)
                        
                        
            #終了
            return
                        
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-p','--pair', type=int, default=4, help='名詞と格助詞のペアの数')
    parser.add_argument('-n','--noun', type=int, default=1, help='各格助詞につく名詞の数')
    parser.add_argument('-hi','--hinum', type=int, default=0, help='格助詞を変更する場所')
    parser.add_argument('-sv','--start_verb', type=int, default=0, help='使用する動詞の頻度の開始順位')
    parser.add_argument('-v','--vc', type=int, default=20, help='生成に使用する候補動詞の数')
    parser.add_argument('-m','--mode', default='all', help='作成する項目')
    parser.add_argument('--unk', default=True, action='store_true', help='名詞を未知語記号にする')
    parser.add_argument('--touten', default=None, action='store_true', help='読点をつける')
    
    args = parser.parse_args()

    main(args)
