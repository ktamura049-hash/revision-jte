#!/bin/bash

#python train_ft4_seibun_pair_kouzou.py
#python train_ft4_seibun_pair_imi.py

for margin in 2 3 4 5 6 7 8 9
do
    python train_ft4_margin_imi_pair.py $margin
done

#for margin in 41 42 43 44 45 46 47 48 49 51 52 53 54 55 56 57 58 59
#do
#    python train_ft4_margin_pair.py $margin
#done
