# japanese-targeted-evaluation
This repository contains data and evaluation code for the following paper:
<論文提出先の学会の情報>

## Requirements
pipでインストールが必要
* [Pytorch](https://pytorch.org/)

基準とする格文法
* [The Kyoto University Case Frame Dictionary](https://nlp.ist.i.kyoto-u.ac.jp/edit.php?%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%A0%BC%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0)

使用する言語モデル
* [rinna japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium)
* [Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative)

## HOW TO USE THIS CODE
### 学習コーパスとテストコーパスの作成

The Kyoto University Case Frame Dictionary(kaku.xml)をgeneratorディレクトリに入れ、下記を実行する

```Bash
cd generator
python bunrui.py > bunresult3.txt
```
すると下記のようなファイル（bunresult3.txt)が得られます

例

`----------------------`

見える 動詞 999

ガ格 555

遠く 555

で格 444

望遠鏡 444

`----------------------`

重なる 動詞 111

ガ格 111

紙 111

`----------------------`

bunresult3.txtをgenerator内の各ディレクトリ内に入れる

各フォルダでそれぞれコマンドを実行

#### grammatical_test_corpus 
```Bash
cd generator/grammatical_test_corpus 
./gen_grammatical_test_corpus.sh
```
validフォルダとtestフォルダが作られる
valid/valid_all.txtはGPT-2のヴァリデーションに使用し、
testフォルダはgrammatical evaluationに使用する

#### semantic_test_corpus
```Bash
cd generator/semantic_test_corpus 
./gen_semantic_test_corpus.sh
```
作成されたtxtファイルをsemantic evaluationに使用する

#### grammatical_training_corpus
```Bash
cd generator/grammatical_training_corpus
./gen_grammatical_training_corpus.sh
```
同階層のhibun_corpusに非文コーパスが作られる

#### semantic_training_corpus
```Bash
cd generator/semantic_training_corpus
./gen_semantic_training_corpus.sh
```
同階層のhibun_corpusに非文コーパスが作られる

### experiment
#### GPT-2
##### fine-tuning
experiment/gpt-2/training にrinna japanese-gpt2-mediumをダウンロードする
```Bash
git clone https://huggingface.co/rinna/japanese-gpt2-medium
```

experiment/gpt-2/trainingに元のテキストファイルとgrammatical_training_corpusとsemantic_training_corpusで非文コーパスを入れる

下記のスクリプトを実行するとファインチューニングが行える
```Bash
./train-margin-pair.sh
```
各エポック毎にbinファイルが作成される

##### evaluation
事前にrinna/pytorch_model.binのコピーを取っておく
作成されたbinファイルでrinnaのpytorch_model.binを上書きする

ヴァリデーションを実施する。gpt2_valid_all_bin.pyを実行すると、結果のjsonファイルが作成される
例）マージン10、エポック3モデルをvalid_all.txtでヴァリデーションを行う
```Bash
python gpt2_valid_all_bin.py rinna valid_all.txt 10 3
```

作成されたjsonファイルの精度を見る
例）probs_medium_margin10.0_3_valid_all.jsonの精度を確認する
```Bash
python gpt2_accuracy_all.py probs_medium_margin10.0_3_valid_all.json
```

もっともよい精度のエポックを確認したら
そのbinファイルでrinna内のPytorch_model.binを上書きする

evaluationを実施する
例）grammatical_test_corpusディレクトリ内のファイルすべてでテストを実行
```Bash
python gpt2_sentence_all_sh_change-bin.py rinna train-ft4_pair_kouzou_10-3 grammatical_test_corpus/*
```

精度を確認する
例）probs_all_margintrain-ft4_pair_kouzou_10.0-0_test_simple_l4h0v20_unk.jsonの精度を確認する
```Bash
python gpt2_accuracy_all_csv_2.py probs_all_margintrain-ft4_pair_kouzou_10.0-0_test_simple_l4h0v20_unk.json 
```

#### LSTM
[Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative)のモデルをDLする
```Bash
git clone https://github.com/aistairc/lm_syntax_negative
```
lm_update内のファイルをlm_syntax_negative/lmに入れる。重複ファイルは上書きする
```Bash
cp lm_update/* lm_syntax_negative/lm
```

##### corpusの準備
###### training corpus
training corpus を作成する
正文用のコーパスとNone非文用のコーパスを用意し、dataディレクトリ内に入れる
二つのコーパスを引数にseihu.pyを実行し、negative-agreementのtxtファイルを作成する
例)train2_100k.txtとnone_train2_100k.txtから作成する場合
```Bash
cd data
python seihu.py train2_100k.txt none_train2_100k.txt >> negative_agreements.train.txt
gzip negative_agreements.train.txt
```
train用のコーパス(train2_100k.txt)とvalidation用コーパス(valid2_10k.txt)のそれぞれで実施し、
negative_agreements.train.txt.gzとnegative_agreements.valid.txt.gzを作成する

trainコーパスとvalidコーパスの名前を変更する
```Bash
mv train2_100k.txt train.txt
mv valid2_10k.txt valid.txt
cp valid.txt test.txt
```

最終的にtraining corpusのディレクトリの中身が下記のようになればOK
*train.txt
*valid.txt
*test.txt
*negative_agreements.train.txt.gz
*negative_agreements.valid.txt.gz

###### test corpus
test corpus はディレクトリ内の同一階層にすべて入れておく必要がある

##### 学習の実行
正文のみを学習させたモデルを作成する
例）grammatical_corpusというディレクトリのtraining corpusを使用する場合
```Bash
cd lm_syntacs_negative
mkdir -p models
python lm/train_lm.py --data grammatical_corpus --save models/lstm.pt --mode sentence \
    --shuffle --length-bucket --non-average --plateau-lr-decay \
    --gpu 0 --seed 1111
```

正文と非文のペアを学習させたモデルを作成する
例）margin 10でgrammatical_corpusというディレクトリのtraining corpusを使用する場合
```Bash
python lm/train_lm.py --data grammatical_corpus --save models/token_margin=10.pt --mode sentagree \
    --neg-mode token --target-syntax agreement \
    --neg-criterion margin --margin 10 \
    --shuffle --length-bucket --non-average --plateau-lr-decay \
    --gpu 0 --seed 1111
```

詳細はNoji and Takamura (2020)の[Training LSTM-LMs](https://github.com/aistairc/lm_syntax_negative?tab=readme-ov-file#training-lstm-lms)と[Training with additional margin losses](https://github.com/aistairc/lm_syntax_negative?tab=readme-ov-file#training-with-additional-margin-losses)を参照。


##### Evaluation
例）model token_margin=10.ptでgrammatical_test_corpusでevaluationを行う場合
```Bash
export LM_OUTPUT=syneval_out/lstm/grammatical/margin10
mkdir -p ${LM_OUTPUT}
python lm/eval.py --model models/token_margin=10.pt --model_type myrnn --template_dir grammatical_test_corpus --myrnn_dir lm --lm_output ${LM_OUTPUT} --capitalize --gpu 0
python analyze/analyze_grammatical.py ${LM_OUTPUT}
```

例）model token_margin=10.ptでsemantic_test_corpusでevaluationを行う場合
```Bash
export LM_OUTPUT=syneval_out/lstm/semantic/margin10
mkdir -p ${LM_OUTPUT}
python lm/eval.py --model models/token_margin=10.pt --model_type myrnn --template_dir semantic_test_corpus --myrnn_dir lm --lm_output ${LM_OUTPUT} --capitalize --gpu 0
python analyze/analyze_semantic.py ${LM_OUTPUT}
```

詳細はNoji and Takamura (2020)の[Syntactic evaluation](https://github.com/aistairc/lm_syntax_negative#syntactic-evaluation)を参照


