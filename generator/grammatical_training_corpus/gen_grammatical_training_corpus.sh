#!/bin/bash

echo "開始"

python corpus2hibun.py train2_100k.txt
python corpus2hibun.py valid2_10k.txt

echo "完了"
