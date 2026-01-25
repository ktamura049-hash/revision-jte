#!/bin/bash

for margin in 200 300 400 500 600 700 800 900
do
    python train_ft4_margin_pair.py $margin
done
