学習コーパスとnoneの非文コーパスからnegative_agreementsを作る
seihu.py train2_100k.txt none_train2_100k.txt > negative_agreements.train.txt
gzip negative_agreements.train.txt
seihu.py valid2_10k.txt none_valid2_10k.txt > negative_agreements.valid.txt
gzip negative_agreements.valid.txt
mv train2_100k.txt train.txt
mv valid2_10k.txt valid.txt
cp valid.txt test.txt