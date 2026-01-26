#!/bin/bash

for i in `seq 0 9`
do
#	cp ./rinna/medium-seibun/train-ft4_seibun_imi_pairjapanese-gpt2-mediumimihibun_not-unk_train2_100k_pe1_$i.bin ./rinna/medium-seibun/pytorch_model.bin
#	echo "copy seibun_imi $i"
#	python gpt2_valid_all_bin.py rinna/medium-seibun not_unk_valid2_10k_test.txt "seibun_imi_pair" $i
	cp ./rinna/medium-seibun/train-ft4_seibun_kouzou_pairjapanese-gpt2-mediumhibun_train2_100k_pe1_$i.bin ./rinna/medium-seibun/pytorch_model.bin
	python gpt2_valid_all_bin.py rinna/medium-seibun test/valid_all_20250511.txt "seibun_kouzou_pair" $i
	echo "copy seibun_kouzou $i"
done

for margin in 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0
do
    for i in `seq 0 9`
    do
#	cp ./rinna/imi-medium/ft-token-margin/train-ft4_pair_japanese-gpt2-mediumimihibun_not-unk_train2_100ktoken-margin_not-unk_imi_pe${margin}_$i.bin ./rinna/imi-medium/ft-token-margin/pytorch_model.bin
	cp ./rinna/medium/ft-token-margin/train-ft4_pairjapanese-gpt2-mediumhibun_train2_100ktoken-margin_pe${margin}_$i.bin ./rinna/medium/ft-token-margin/pytorch_model.bin
	echo "copy margin $margin $i"
#	python gpt2_valid_all_bin.py rinna/imi-medium/ft-token-margin not_unk_valid2_10k_test.txt $margin $i
	python gpt2_valid_all_bin.py rinna/medium/ft-token-margin test/valid_all_20250511.txt $margin $i
    done
done
