# Japanese-targeted-evaluation
This repository contains data and evaluation code for the following paper:  
<Information about the conference/journal to which the paper is submitted>

## Requirements
The following must be installed via pip:
* [PyTorch](https://pytorch.org/)

Case grammar:
* [The Kyoto University Case Frame Dictionary](https://nlp.ist.i.kyoto-u.ac.jp/edit.php?%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%A0%BC%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0)

Language models:
* [rinna japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium)
* [Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative)

## Creating training and test corpora

Place The Kyoto University Case Frame Dictionary (`kaku.xml`) in the `generator` directory and run the following:

```Bash
cd generator
python bunrui.py > bunresult3.txt
```

This will produce a file like the following (`bunresult3.txt`):

Example:

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

Place `bunresult3.txt` into each directory under `generator`.

Run the following command in each folder.

### grammatical_test_corpus 
```Bash
cd generator/grammatical_test_corpus 
./gen_grammatical_test_corpus.sh
```

The `valid` and `test` directories will be created.  
`valid/valid_all.txt` is used for GPT-2 validation, and  
the `test` directory is used for grammatical evaluation.

### semantic_test_corpus
```Bash
cd generator/semantic_test_corpus 
./gen_semantic_test_corpus.sh
```

Use the generated txt files for semantic evaluation.

### grammatical_training_corpus
```Bash
cd generator/grammatical_training_corpus
./gen_grammatical_training_corpus.sh
```

An ungrammatical corpus will be created in `hibun_corpus` at the same directory level.

### semantic_training_corpus
```Bash
cd generator/semantic_training_corpus
./gen_semantic_training_corpus.sh
```

An ungrammatical corpus will be created in `hibun_corpus` at the same directory level.

## experiment
### GPT-2
#### fine-tuning
Download `rinna japanese-gpt2-medium` into `experiment/gpt-2/training`:

```Bash
git clone https://huggingface.co/rinna/japanese-gpt2-medium
```

Place the original text files and the ungrammatical corpora generated from  
`grammatical_training_corpus` and `semantic_training_corpus` into  
`experiment/gpt-2/training`.

Run the following script to perform fine-tuning:

```Bash
./train-margin-pair.sh
```

A `.bin` file will be created for each epoch.

#### evaluation
Make a backup copy of `rinna/pytorch_model.bin` beforehand.  
Overwrite `rinna/pytorch_model.bin` with the generated `.bin` file.

Run validation. Executing `gpt2_valid_all_bin.py` will generate a JSON file with results.

Example: validating a model with margin 10 and epoch 3 using `valid_all.txt`:

```Bash
python gpt2_valid_all_bin.py rinna valid_all.txt 10 3
```

Check the accuracy of the generated JSON file.

Example: checking the accuracy of `probs_medium_margin10.0_3_valid_all.json`:

```Bash
python gpt2_accuracy_all.py probs_medium_margin10.0_3_valid_all.json
```

After identifying the epoch with the best accuracy,  
overwrite `Pytorch_model.bin` in `rinna` with that `.bin` file.

Run evaluation.

Example: running tests on all files in the `grammatical_test_corpus` directory:

```Bash
python gpt2_sentence_all_sh_change-bin.py rinna train-ft4_pair_kouzou_10-3 grammatical_test_corpus/*
```

Check accuracy.

Example: checking the accuracy of  
`probs_all_margintrain-ft4_pair_kouzou_10.0-0_test_simple_l4h0v20_unk.json`:

```Bash
python gpt2_accuracy_all_csv_2.py probs_all_margintrain-ft4_pair_kouzou_10.0-0_test_simple_l4h0v20_unk.json 
```

### LSTM
Download the model from [Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative):

```Bash
git clone https://github.com/aistairc/lm_syntax_negative
```

Place the files in `lm_update` into `lm_syntax_negative/lm`, overwriting duplicates:

```Bash
cp lm_update/* lm_syntax_negative/lm
```

#### Preparing corpora
##### training corpus
Create the training corpus.  
Prepare a corpus of grammatical sentences and a corpus of ungrammatical sentences (None type),  
and place them in the `data` directory.

Run `seihu.py` with the two corpora as arguments to create a negative-agreement txt file.

Example: creating from `train2_100k.txt` and `none_train2_100k.txt`:

```Bash
cd data
python seihu.py train2_100k.txt none_train2_100k.txt >> negative_agreements.train.txt
gzip negative_agreements.train.txt
```

Do this separately for the training corpus (`train2_100k.txt`) and  
the validation corpus (`valid2_10k.txt`) to create  
`negative_agreements.train.txt.gz` and `negative_agreements.valid.txt.gz`.

Rename the training and validation corpora:

```Bash
mv train2_100k.txt train.txt
mv valid2_10k.txt valid.txt
cp valid.txt test.txt
```

The final contents of the training corpus directory should look like this:

* train.txt  
* valid.txt  
* test.txt  
* negative_agreements.train.txt.gz  
* negative_agreements.valid.txt.gz  

##### test corpus
All test corpus files must be placed at the same directory level.

#### Running training
Create a model trained only on grammatical sentences.

Example: using the training corpus in a directory named `grammatical_corpus`:

```Bash
cd lm_syntacs_negative
mkdir -p models
python lm/train_lm.py --data grammatical_corpus --save models/lstm.pt --mode sentence \
    --shuffle --length-bucket --non-average --plateau-lr-decay \
    --gpu 0 --seed 1111
```

Create a model trained on grammatical–ungrammatical sentence pairs.

Example: using margin 10 with the training corpus in `grammatical_corpus`:

```Bash
python lm/train_lm.py --data grammatical_corpus --save models/token_margin=10.pt --mode sentagree \
    --neg-mode token --target-syntax agreement \
    --neg-criterion margin --margin 10 \
    --shuffle --length-bucket --non-average --plateau-lr-decay \
    --gpu 0 --seed 1111
```

For details, see  
[Training LSTM-LMs](https://github.com/aistairc/lm_syntax_negative?tab=readme-ov-file#training-lstm-lms) and  
[Training with additional margin losses](https://github.com/aistairc/lm_syntax_negative?tab=readme-ov-file#training-with-additional-margin-losses)  
in Noji and Takamura (2020).

#### Evaluation
Example: evaluating `token_margin=10.pt` on `grammatical_test_corpus`:

```Bash
export LM_OUTPUT=syneval_out/lstm/grammatical/margin10
mkdir -p ${LM_OUTPUT}
python lm/eval.py --model models/token_margin=10.pt --model_type myrnn --template_dir grammatical_test_corpus --myrnn_dir lm --lm_output ${LM_OUTPUT} --capitalize --gpu 0
python analyze/analyze_grammatical.py ${LM_OUTPUT}
```

Example: evaluating `token_margin=10.pt` on `semantic_test_corpus`:

```Bash
export LM_OUTPUT=syneval_out/lstm/semantic/margin10
mkdir -p ${LM_OUTPUT}
python lm/eval.py --model models/token_margin=10.pt --model_type myrnn --template_dir semantic_test_corpus --myrnn_dir lm --lm_output ${LM_OUTPUT} --capitalize --gpu 0
python analyze/analyze_semantic.py ${LM_OUTPUT}
```

For details, see  
[Syntactic evaluation](https://github.com/aistairc/lm_syntax_negative#syntactic-evaluation)  
in Noji and Takamura (2020).
