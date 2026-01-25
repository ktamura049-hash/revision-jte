#!/bin/bash
# validを解析するスクリプト
version=20250511
filename=result_${version}_valid_margin1-900.txt

rm $filename

for margin in 1.0 10.0 100.0 1000.0 20.0 30.0 40.0 50.0 60.0 70.0 80.0 90.0 200.0 300.0 400.0 500.0 600.0 700.0 800.0 900.0
#for margin in 1.0 10.0 100.0 1000.0
do
    python gpt2_accuracy_all.py *${margin}*valid_all_${version}.json >> $filename
    echo $margin
done

less $filename | grep -E "json|総数"
