# japanese-targeted-evaluation
This repository contains data and evaluation code for the following paper:
～～～～～～～～～～

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
python bunrui.py > bunresult3.txt
```
すると下記のようなファイル（bunresult3.txt)が得られます

例
----------------------
見える　動詞　111
ガ格　111
----------------------
見える　動詞　111
ヲ格　111
----------------------

bunresult3.txtをgenerator内の各ディレクトリ内に入れる

各フォルダでそれぞれコマンドを実行

#### grammatical_test_corpus 
```Bash
./gen_corpus.sh
```
validフォルダとtestフォルダが作られる
valid/valid_all.txtはGPT-2のヴァリデーションに使用し、
testフォルダはそのままgrammatical evaluationに使用する

#### semantic_test_corpus
```Bash
./gen_semantic_test_corpus.sh
```
作成されたtxtファイルをsemantic evaluationに使用する

#### grammatical_training_corpus
```Bash
./gen_grammatical_training_corpus.sh
```
同階層のhibun_corpusに非文コーパスが作られる

#### semantic_training_corpus
```Bash
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

experiment/gpt-2/trainingに元のテキストファイルとgrammatical_training_corpusとsemantic_training_corpusを

下記のスクリプトを実行するとファインチューニングが行える
```Bash
./train-margin-pair.sh
```
各エポック毎にbinファイルが作成される

##### evaluation

作成されたbinファイルをrinnaのpytorch_model.binと挿げ替える

ヴァリデーションを実施する。下記のコマンドを実行。結果のjsonファイルが作成される
```Bash
python gpt2_valid_all_bin.py rinna valid_file margin epoch
```

作成されたjsonファイルを下記のコマンドで精度を見る
```Bash
python gpt2_accuracy_all.py json_file
```

もっともよい精度のエポックを確認したら
再度rinna内のPytorch_model.binとそのbinファイルを挿げ替える

コマンドを実行し結果のjsonファイル作成
```Bash
python gpt2_sentence_all_sh_change-bin.py rinna/medium/ft-token-margin train-ft4_pair_kouzou_${margin[ix]}-${epoch[ix]} test/test_all_$day/*
```

最終的な精度を確認する
```Bash
./accuracy.sh margin