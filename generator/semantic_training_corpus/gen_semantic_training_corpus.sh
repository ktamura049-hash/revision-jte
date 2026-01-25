#!/bin/bash

corpus="train2_100k_not-unk.txt"

echo "開始"

python kakushuffle_training.py ${corpus}


echo "完了"
