# Japanese-targeted-evaluation
This repository contains data and evaluation code for the following paper:  
<Information about the conference/journal to which the paper is submitted>

## Requirements
The following must be installed via pip:
* [PyTorch](https://pytorch.org/)
* [TensorFlow](https://www.tensorflow.org/)
* [Transformers](https://huggingface.co/docs/transformers/index)
* [MeCab](https://www.mlab.im.dendai.ac.jp/~yamada/ir/MorphologicalAnalyzer/MeCab.html)

Case grammar:
* [The Kyoto University Case Frame Dictionary](https://nlp.ist.i.kyoto-u.ac.jp/edit.php?%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%A0%BC%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0)

Language models:
* [rinna japanese-gpt2-medium](https://huggingface.co/rinna/japanese-gpt2-medium)
* [Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative)


## Setting experiment path
After downloading the repository, set the absolute path of the folder as an environment variable:

```Bash
cd japanese-targeted-evaluation
export EXPERIMENT_PATH="$(pwd)"
```

This ensures that the program can consistently reference the directory regardless of the current working directory.

## Creating training and test corpora

Place The Kyoto University Case Frame Dictionary (`kaku.xml`) in the `generator` directory and run the following:

```Bash
cd EXPERIMENT_PATH/generator
python bunrui.py > bunresult.txt
```

This will produce a file like the following (`bunresult3.txt`):

Example:

`----------------------`

見える 動1 999  

ガ格 555  

遠く 555  

で格 444  

望遠鏡 444  

`----------------------`

重なる 動1 111  

ガ格 111  

紙 111  

`----------------------`

Place `bunresult.txt` into each directory under `generator`.

Run the following command in each folder.

### grammatical_test_corpus 
```Bash
cd EXPERIMENT_PATH/generator/grammatical_test_corpus 
./gen_grammatical_test_corpus.sh
```

For grammatical evaluation, the `valid` and `test` directories are created.  
`valid/valid_all.txt` is used for GPT-2 validation.

### semantic_test_corpus
```Bash
cd EXPERIMENT_PATH/generator/semantic_test_corpus 
./gen_semantic_test_corpus.sh
```

The created text file is used semantic evaluation.(あとでGPTに聞く)

### grammatical_training_corpus
```Bash
cd EXPERIMENT_PATH/generator/grammatical_training_corpus
./gen_grammatical_training_corpus.sh
```

Ungrammatical corpora are created in `hibun_corpus`.

### semantic_training_corpus
```Bash
cd EXPERIMENT_PATH/generator/semantic_training_corpus
./gen_semantic_training_corpus.sh
```

Ungrammatical corpora are created in `hibun_corpus`.

## Experiment
### GPT-2
#### Fine-tuning
Download `rinna japanese-gpt2-medium` into `experiment/gpt-2/training`:

```Bash
cd EXPERIMENT_PATH/experiment/gpt-2/training
git clone https://huggingface.co/rinna/japanese-gpt2-medium
```

Place the original text files and the ungrammatical corpora generated from  
`grammatical_training_corpus` and `semantic_training_corpus` into  
`experiment/gpt-2/training`.

```Bash
mv EXPERIMENT_PATH/generator/grammatical_traning_corpus/*train2_100k.txt EXPERIMENT_PATH/experiment/gpt-2/training/
mv EXPERIMENT_PATH/generator/semantic_traning_corpus/*train2_100k.txt EXPERIMENT_PATH/experiment/gpt-2/training/
```

Run the following script to perform fine-tuning:

```Bash
cd EXPERIMENT_PATH/experiment/gpt-2/training/
./train-margin-pair.sh
```

A `.bin` file is created for each epoch.

#### Evaluation
Overwrite `rinna/pytorch_model.bin` with the generated `.bin` file in fine-tuning.

Run validation. 

For grammatical

```Bash
cd EXPERIMENT_PATH/experiment/gpt-2/
./valid.sh
./accuracy_valid.sh
```

Use the best epoch for evaluation.

Run evaluation.

Running tests on all files in the `grammatical_test_corpus` directory.

Example: running tests on margin10 epoch3

```Bash
./grammatical_eval.sh 10 3
```

The same procedure can be applied for semantic evaluation.
Apply semantic_eval.sh instead of grammtical_eval.sh

### LSTM
Download the model from [Noji and Takamura (2020)](https://github.com/aistairc/lm_syntax_negative):

```Bash
cd EXPERIMENT_PATH/experiment/lstm
git clone https://github.com/aistairc/lm_syntax_negative
```

Place the files in `lm_update` into `lm_syntax_negative/lm`, overwriting duplicate files:

```Bash
cp lm_update/* lm_syntax_negative/lm
```

#### Preparing corpora
##### Training corpora
Create the training corpora.  
Prepare a corpus of grammatical sentences and a corpus of ungrammatical sentences,  
and place them in the `data` directory.

```Bash
cd EXPERIMENT_PATH/experiment/lstm/data
./create_grammatical_corpora.sh
./create_semantic_corpora.sh
```

The final contents of the training corpus directory are:

* train.txt  
* valid.txt  
* test.txt  
* negative_agreements.train.txt.gz  
* negative_agreements.valid.txt.gz  

##### Test corpora
Move the test corpora to `/experiment/lstm/`

```Bash
cp EXPERIMENT_PATH/generator/grammatical_test_corpus/test EXPERIMENT_PATH/experiment/lstm/grammatical_test_corpus
mkdir -p EXPERIMENT_PATH/experiment/lstm/semantic_test_corpus
cp EXPERIMENT_PATH/generator/semantic_test_corpus/test2_test.txt EXPERIMENT_PATH/experiment/lstm/semantic_test_corpus/
```

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

Create a model trained on grammatical and ungrammatical sentence pairs.

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
