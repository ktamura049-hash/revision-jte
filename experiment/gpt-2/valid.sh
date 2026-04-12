#!/bin/bash

grammatical_valid.sh


# validation for only correct sentence 
for i in `seq 0 9`
do
	# grammatical
	cp ./train/train-ft4_seibun_kouzou_pairjapanese-gpt2-mediumhibun_train2_100k_pe1_$i.bin ./rinna/medium/pytorch_model.bin
	echo "copy correct grammatical $i"
	python gpt2_valid_all_bin.py rinna/medium valid_all.txt "corerct_grammatic_pair" $i
	echo "correct grammatical eval $i"

	# semantic
	cp ./train/train-ft4_seibun_imi_pairjapanese-gpt2-mediumhibun_not-unk_train2_100k_pe1_$i.bin ./rinna/medium/pytorch_model.bin
	echo "copy correct semantic $i"
	python gpt2_valid_all_bin.py rinna/medium not_unk_valid2_10k_test.txt "correct_semantic_pair" $i
	echo "correct semantic eval $i"
done


# validation for multi-margin-loss
for margin in 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0
do
    for i in `seq 0 9`
    do
	# grammatical
	cp ./train/ft-token-margin/train-ft4_pairjapanese-gpt2-mediumhibun_train2_100ktoken-margin_pe${margin}_$i.bin ./rinna/medium/pytorch_model.bin
	echo "copy grammatical margin $margin $i"
	python gpt2_valid_all_bin.py rinna/medium not_unk_valid2_10k_test.txt $margin $i
	echo "correct grammatical eval $i"

	# semantic
	cp ./train/ft-token-margin/train-ft4_pair_japanese-gpt2-mediumhibun_not-unk_train2_100ktoken-margin_not-unk_imi_pe${margin}_$i.bin ./rinna/medium/pytorch_model.bin
	echo "copy semantic margin $margin $i"
	python gpt2_valid_all_bin.py rinna/medium valid_all.txt $margin $i
	echo "correct semantic eval $i"
    done
done
