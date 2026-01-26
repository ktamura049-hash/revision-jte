#!/bin/bash

echo "開始"

python kakushuffle_training.py "not-unk_train2_100k.txt"
python kakushuffle_training.py "not_unk_valid2_10k.txt"

echo "完了"
