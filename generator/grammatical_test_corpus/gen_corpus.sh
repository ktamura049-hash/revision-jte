#!/bin/bash
# 構造評価用テストコーパスを作成

# ループ
for i in 0 1 2 3
do
    mkdir l4h$i
    #ファイル作成
    python create_sentence.py -hi $i
    mv *l4h$i*.txt ./l4h$i
    # validとtestに分ける
    python sort_vt.py l4h$i
done

valid_path="./valid_corpus"
save_file="valid_all.txt"
rm ${valid_path}/${save_file}
for filename in ${valid_path}/*.txt
do
    cat ${filename} >> ${valid_path}/${save_file}
done
