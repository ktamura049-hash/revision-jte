#!/bin/bash
# validを解析するスクリプト
corgram_filename=result_grammtical_valid_correct.txt
corsem_filename=result_semantic_valid_correct.txt
mmgram_filename=result_grammatical_valid_margin1-10.txt
mmsem_filename=result_semantic_valid_margin1-10.txt

rm $corgram_filename
rm $corsem_filename
rm $mmgram_filename
rm $mmsem_filename

# correct
python gpt2_accuracy_all.py *corerct_grammatic_pair*.json >> $corgram_filename 
python gpt2_accuracy_all.py *correct_semantic_pair*.json >> $corsem_filename
echo "done correct"

# multi-margin
for margin in 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0
do
    python gpt2_accuracy_all.py *${margin}*valid_all.json >> $mmgram_filename
    python gpt2_accuracy_all.py *${margin}*not_unk_valid2_10k_test.json >> $mmgram_filename
    echo $margin
done

# 結果の表示
less $corgram_filename| grep -E "json|総数"
less $corsem_filename| grep -E "json|総数"
less $mmgram_filename| grep -E "json|総数"
less $mmsem_filename| grep -E "json|総数"