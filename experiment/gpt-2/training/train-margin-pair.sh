#!/bin/bash

python train_ft4_seibun_pair_kouzou.py
python train_ft4_seibun_pair_imi.py

for margin in 1 2 3 4 5 6 7 8 9 10
do
    python train_ft4_margin_imi_pair.py $margin
    python train_ft4_margin_pair.py $margin
done
