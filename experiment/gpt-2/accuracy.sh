#!/bin/bash

filename=result_20250303_test_$1.txt
rm $filename

# 結果を記録する
for test_case in simple complex_adv complex_adj complex_sup
do
    python gpt2_accuracy_all_csv_2.py *$1*test_${test_case}*l4h*.json >> $filename
    echo ${test_case}
done

#less $filename | grep -E "json|総数"
# 結果を整理する
python result_seiri.py $filename
