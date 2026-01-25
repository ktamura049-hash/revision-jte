#!/bin/bash

corpus="test2.txt"

echo "開始"

python kakushuffle3.py ${corpus}
python marge_test_sh.py ${corpus}

echo "完了"
