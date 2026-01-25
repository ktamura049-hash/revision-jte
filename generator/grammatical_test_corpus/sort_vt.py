#-*- coding:utf-8 -*-
#sort_vt.py

#生成された文をvalid用とテスト用に分ける

from kakutaple4 import cdict
from kakuseiri3 import kakuhyou, kakuhenkan
import sys
import os
import random
import copy
import io
import itertools
import glob
from cre_sent import save_sentence


# 保存先のフォルダやパスを作る
def create_save_path(path):
    filename = path.split('/')[-1]
    valid_folder = 'valid_corpus'
    test_folder = 'test_corpus'
    os.makedirs(valid_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)
    save_valid_path = os.path.join(valid_folder, 'valid_'+filename)
    save_test_path = os.path.join(test_folder, 'test_'+filename)
    if os.path.exists(save_valid_path):
        os.remove(save_valid_path)
    if os.path.exists(save_test_path):
        os.remove(save_test_path)

    return save_valid_path, save_test_path

# 単文のときのvalid,testデータの作成
def sort_simple(path):
    save_valid_path, save_test_path = create_save_path(path)
    #ファイル名にlが入ってたら、lの次の文字を格助詞と名詞のペアの数とする
    for i in range(len(path)):
        if path[i] == 'l' :
            #length：格助詞と名詞のペアの数
            length = path[i+1]
        if path[i] == 'n' :
            #namelen：各格助詞につく名詞の数
            namelen = path[i+1]
        else :
            namelen = 1

    # ファイル名から動詞の数を取得し、2等分する
    num_verb = int(path.replace('v','_').split('_')[-2])
    #valid_len = int(num_verb / 2)
    #test_len = int(num_verb - valid_len)

    #part：各動詞が何ペア生成されているかを計算する変数。
    #ファイル名にunkが入っていたら＝名詞を<unk>に置換していたら
    if 'unk' in path:
        part = 1
        #単文のunkのファイルはパーテーションしているため、各動詞につき、
        #length!個のペアとなる
        for i in range(1,int(length)+1):
            part = part * i
    
    #unkが入っていない＝名詞を使用していたら
    else:
        #「各格助詞に付く名詞の数」の「格助詞と名詞のペアの数」個のペアになる
        part = namelen**(int(length))
    
    #print(length,part, 20*part)
    
    #　動詞の取得
    with open('./use_verb.txt') as f:
        verbs = [s.strip() for s in f.readlines()]
        print(verbs)
        
    # validファイルに入れるペアの量
    num_valid = 5
        
    # 作成した文を取得
    with open(path) as f:
        sentence = [s.strip() for s in f.readlines()]

    # 作成したペアのIDリストを作成
    pair_ids = [range(int(len(sentence)/2))]

    # 各動詞ごとに取得
    for i in range(len(verbs)):
        print('-'*50)
        print(i, verbs[i])
        print('-'*50)

        # その動詞のペアIDの範囲からvalidに使う文を取得。それ以外はテストのペアにする
        each_pair_ids = range(part*i,part*(i+1))
        valid_pair_ids = random.sample(each_pair_ids, num_valid)
        test_pair_ids = set(each_pair_ids) - set(valid_pair_ids)

        # validに選んだペアを書き込み
        for each_valid in valid_pair_ids:
            # 正文
            save_sentence(save_valid_path, sentence[2*each_valid])
            # 非文
            save_sentence(save_valid_path, sentence[2*each_valid+1])
            
        # testに選んだペアを書き込み
        for each_test in test_pair_ids:
            # 正文
            save_sentence(save_test_path, sentence[2*each_test])
            # 非文
            save_sentence(save_test_path, sentence[2*each_test+1])

                
# 複文の時のvalid,testデータの作成
def sort_complex(path):

    save_valid_path, save_test_path = create_save_path(path)
        
    #動詞の組み合わせ数
    num_verb = int(path.replace('v','_').split('_')[-2])
    kumiawase = num_verb * (num_verb-1)

    print(kumiawase)
    
    #item = 節の項目数
    #連用節　並列節、テ節、条件節、理由節、時間節で5つ
    if 'adv_' in path:
        item = 5
    #連体節　無標、有標で2つ
    elif 'adj_' in path:
        item = 2
    #補足節　現状補足節のみ
    elif 'sup_' in path:
        item = 1

    # 作成した文の取得
    with open(path) as f:
        sentence = [s.strip() for s in f.readlines()]

    # 作成したペアのIDリストを作成
    pair_ids = [range(int(len(sentence)/2))]

    # validに使うペア数
    num_valid = 100

    # 節の各項目の数だけ行う
    for ram in range(item):
        # その動詞のペアIDの範囲からvalidに使う文を取得。それ以外はテストのペアにする
        each_pair_ids =range(ram*kumiawase,(ram+1)*kumiawase)
        print(len(each_pair_ids), int(num_valid/item))
        valid_pair_ids = random.sample(each_pair_ids, int(num_valid/item))
        print(valid_pair_ids)
        test_pair_ids = set(each_pair_ids) - set(valid_pair_ids)
        print(test_pair_ids)
        
        # validに選んだペアを書き込み
        for each_valid in valid_pair_ids:
            # 正文
            save_sentence(save_valid_path, sentence[2*each_valid])
            # 非文
            save_sentence(save_valid_path, sentence[2*each_valid+1])
            
        # testに選んだペアを書き込み
        for each_test in test_pair_ids:
            # 正文
            save_sentence(save_test_path, sentence[2*each_test])
            # 非文
            save_sentence(save_test_path, sentence[2*each_test+1])
            

                
if __name__ == '__main__':
    # フォルダーを引数で受け取る
    folder_path = os.listdir(sys.argv[1])
    for files in folder_path:
        print(files)
        file_path = os.path.join(sys.argv[1],files)
        print(file_path)
        if "simple" in files:
            sort_simple(file_path)
        elif "complex" in files:
            sort_complex(file_path)
