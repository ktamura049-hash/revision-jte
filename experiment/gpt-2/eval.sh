#!/bin/bash

day=20250511
margin=0

# rinnaのそのまま
#python gpt2_sentence_all_sh_change-bin.py rinna/japanese-gpt2-medium rinna_pair_kouzou_ test/test_all_$day/*

#正文のみのeval
#cp ./rinna/medium-seibun/train-ft4_seibun_kouzou_pairjapanese-gpt2-mediumhibun_train2_100k_pe1_$margin.bin ./rinna/medium-seibun/pytorch_model.bin
#echo "copy seibun kouzou"
#python gpt2_sentence_all_sh_change-bin.py rinna/medium-seibun train-ft4_seibun_kouzou-$margin test/test_all_$day/*

#cp ./rinna/medium-seibun/train-ft4_seibun_imi_pairjapanese-gpt2-mediumimihibun_not-unk_train2_100k_pe1_4.bin ./rinna/medium-seibun/pytorch_model.bin
#echo "copy seibun imi"
#python gpt2_sentence_all_sh_change-bin.py rinna/imi-medium/ft-token-margin train-ft4_seibun_imi-4 test/not-unk_random_change_same_test2.txt

#意味eval
#margin=(11.0 12.0 13.0 14.0 15.0 16.0 17.0 18.0 19.0 21.0 22.0 23.0 24.0 25.0 26.0 27.0 28.0 29.0)
#epoch=(2 2 1 2 9 9 9 9 9 5 9 5 6 8 0 6 6 6) 

#margin=(0.01 0.1 1.0 10.0 100.0 1000.0)
#epoch=(3 3 3 1 0 0)

#margin=(20.0 30.0 40.0 50.0 60.0 70.0 80.0 90.0)
#epoch=(9 9 9 0 0 0 0 0)

#for ix in ${!margin[@]}
#do
#    cp ./rinna/imi-medium/ft-token-margin/train-ft4_pair_japanese-gpt2-mediumimihibun_not-unk_train2_100ktoken-margin_not-unk_imi_pe${margin[ix]}_${epoch[ix]}.bin ./rinna/imi-medium/ft-token-margin/pytorch_model.bin
#    echo "copy imi ${margin[ix]} ${epoch[ix]}"
#    python gpt2_sentence_all_sh_change-bin.py rinna/imi-medium/ft-token-margin train-ft4_pair_imi_${margin[ix]}-${epoch[ix]} test/not-unk_random_change_same_test2.txt
#done

#構造eval
#margin=(1.0 10.0 100.0 1000.0)
#epoch=(0 0 1 1)

#margin=(1.0 10.0 100.0 1000.0 20.0 30.0 40.0 50.0 60.0 70.0 80.0 90.0 200.0 300.0 400.0 500.0 600.0 700.0 800.0 900.0)
#epoch=(0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1)

margin=(600.0 700.0 800.0 900.0)
epoch=(1 1 1 1)

for ix in ${!margin[@]}
do
    cp ./rinna/medium/ft-token-margin/train-ft4_pairjapanese-gpt2-mediumhibun_train2_100ktoken-margin_pe${margin[ix]}_${epoch[ix]}.bin ./rinna/medium/ft-token-margin/pytorch_model.bin
    echo "copy kouzou ${margin[ix]} ${epoch[ix]}"
    python gpt2_sentence_all_sh_change-bin.py rinna/medium/ft-token-margin train-ft4_pair_kouzou_${margin[ix]}-${epoch[ix]} test/test_all_$day/*
done
