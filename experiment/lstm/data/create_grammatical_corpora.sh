FOLDER="grammatical_corpus"

mkdir -p $FOLDER

seihu.py train2_100k.txt none_train2_100k.txt > negative_agreements.train.txt
gzip negative_agreements.train.txt
mv negative_agreements.train.txt.gz $FOLDER/
seihu.py valid2_10k.txt none_valid2_10k.txt > negative_agreements.valid.txt
gzip negative_agreements.valid.txt
mv negative_agreements.valid.txt.gz $FOLDER/ 
cp train2_100k.txt $FOLDER/train.txt
cp valid2_10k.txt  $FOLDER/valid.txt
cp valid2_10k.txt  $FOLDER/test.txt