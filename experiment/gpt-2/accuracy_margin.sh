#!/bin/bash

# 指定したマージンの精度を出す
for margin in seibun 1.0 2.0 3.0 4.0 5.0 6.0 7.0 0.0 9.0 10.0
do
    ./accuracy.sh $margin
done
