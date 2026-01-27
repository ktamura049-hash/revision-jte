#!/bin/bash

day="20250511_"

for margin in $@
do
    echo ${margin}
    python result_seiri.py result_kouzou_${day}margin\=${margin}.json
done

