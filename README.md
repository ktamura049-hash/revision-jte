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
#### semantic_test_corpus
```Bash
./gen_semantic_test_corpus.sh
```

#### grammatical_training_corpus
corpus2hibun.py に引数でコーパスを与えることで、自然文から
```Bash
python corpus2hibun.py train2_100k.txt
python corpus2hibun.py valid2_10k.txt
```
