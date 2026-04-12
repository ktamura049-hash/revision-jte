#!/bin/bash

# evaluate
cp ./train/train-ft4_pair_japanese-gpt2-mediumtrain2_100ktoken-margin_pe${1}.0_${2}.bin ./rinna/japanese-gpt2-medium/pytorch_model.bin
echo "copy grammatical margin $1 epoch $2"
python gpt2_sentence_all_sh_change-bin.py rinna train-ft4_pair_grammatical_${1}.0-${2} grammatical_test_corpus/*

# print accuracy
python gpt2_accuracy_all_csv_2.py probs_all_margintrain-ft4_pair_grammatical_${1}.0-${2}_*.json | grep -E "json|total_num"

