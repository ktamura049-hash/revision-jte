#eval.py
#格助詞のやつ
# -*- coding:utf-8 -*-

import argparse
import gzip
import logging
import torch

import batch_generator
import data
import evaluator
import train_lm
import utils

import argparse
import logging
import pickle
import os
import subprocess
import operator
from progress.bar import Bar
#from tester.TestWriter import TestWriter
#from template.TestCases import TestCase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s: %(message)s')


#引数の設定
parser = argparse.ArgumentParser(description="Parameters for testing a language model")

parser.add_argument('--template_dir', type=str, default='../EMNLP2018/templates',
                                        help='Location of the template files')
parser.add_argument('--output_file', type=str, default='all_test_sents.txt',
                                        help='File to store all of the sentences that will be tested')
parser.add_argument('--model', type=str, default='../models/model.pt',
                                        help='The model to test')
parser.add_argument('--lm_data', type=str, default='../models/model.bin',
                                        help='The model .bin file that accompanies the model (for faster loading)')
parser.add_argument('--tests', type=str, default='all',
                                        help='Which constructions to test (agrmt/npi/all)')
parser.add_argument('--model_type', type=str, required=True,
                                        help='Which kind of model (RNN/multitask/ngram/myRNN)')
parser.add_argument('--unit_type', type=str, default='word',
                                        help='Kinds of units used osyneval_out/lstmn language model (word/char)')
parser.add_argument('--ngram_order', type=int, default=5,
                                        help='Order of the ngram model')
parser.add_argument('--vocab', type=str, default='ngram_vocab.pkl',
                                        help='File containing the ngram vocab')
parser.add_argument('--myrnn_dir', type=str, help='Path to lm directory for my rnn')
parser.add_argument('--lm_output', type=str, default='lm_output',
                                        help='Path to directory where result files are saved')
#parser.add_argument('--gpu', type=int, default=None)
parser.add_argument('--capitalize', action='store_true')

args = parser.parse_args()


def load_model(fn, device=None):
    with open(fn, 'rb') as f:
        modelwrap, optimizer = torch.load(f)
        assert isinstance(modelwrap, model_wrapper.RNNModelWrapper)
    return modelwrap, optimizer

def run_test(args, device):
    batch_size = args.batch_size
    rnn, optimizer = train_lm.load_model(args.model, device)
    vocab = rnn.vocab
    pad_id = vocab.index(data.PAD)
    
    ev = evaluator.SentenceEvaluator(pad_id)
    
    sents = data.read_sentences(args.data, False, False, vocab.start_symbol, args.sentence_piece_model)
    if args.ignore_eos:
        assert sents[0][-2] == sents[0][-1] == data.EOS
        sents = [s[:-1] for s in sents] # remove dupicated EOS
    if args.capitalize:
        for sent in sents:
            sent[1] = sent[1].capitalize()
            
    tensors = data.to_tensors(sents, vocab)
    batch_gen = batch_generator.SentenceBatchGenerator(tensors, batch_size, pad_id)
    calc_entropy = not args.no_entropy
    if calc_entropy:
        logger.info('calc entropy')
    else:
        logger.info('not calc entropy')
        
    print('First sentences (after conversion):')
    for s in tensors[:3]:
        print(' '.join([vocab.value(t) for t in s]))
        
    def open_for_w(fn):
        if fn.endswith('.gz'):
            return gzip.open(fn, 'wt')
        else:
            return open(fn, 'w')
        
    def resolve_subwords(pieces, piece_surps, piece_ents):
        word_sent = []
        sent_surps = []
        sent_ents = []
        is_intermediate = False
        for i, piece in enumerate(pieces):
            if is_intermediate:
                if '_' in piece:
                    word_sent[-1] += piece[:-1]
                    is_intermediate = False
                else:
                    word_sent[-1] += piece
                    sent_surps[-1] += piece_surps[i]
            else:
                if '_' in piece:
                    word_sent.append(piece[:-1])
                else:
                    word_sent.append(piece)
                    is_intermediate = True
                sent_surps.append(piece_surps[i])
                sent_ents.append(piece_ents[i])
            
        return word_sent, sent_surps, sent_ents

    with open_for_w(args.output) as o:
        if args.internal_token:
            o.write("word processed sentid sentpos wlen surp entropy\n")
            
            def report(word, sent_i, j, sent_surps, sent_ents):
                # transform-to-id-then-detransform results in the internal string rep.
                conved = vocab.value(vocab.index_unked(word))
                return '{} {} {} {} {} {} {}\n'.format(
                    word, conved, sent_i, j, len(word), sent_surps[j], sent_ents[j])
        else:
            o.write("word sentid sentpos wlen surp entropy\n")
            
            def report(word, sent_i, j, sent_surps, sent_ents):
                return '{} {} {} {} {} {}\n'.format(
                    word, sent_i, j, len(word), sent_surps[j], sent_ents[j])
        o.write("\n")

        sent_i = 0
        
        total_batchs = len(tensors) // batch_size
        for batch_i, i in enumerate(range(0, len(tensors), batch_size)):
            if batch_i > 0 and batch_i % 100 == 0:
                logger.info("{}/{} batches processed.".format(batch_i, total_batchs))
            sources = tensors[i:i+batch_size]
            with torch.no_grad():
                surps, entropys = ev.word_stats(rnn, sources, pad_id, calc_entropy=calc_entropy)

            for sent_surps, sent_ents in zip(surps, entropys):
                sent = sents[sent_i][1:] # remove begin of sentence
                if args.sentence_piece_model is not None:
                    sent, sent_surps, sent_ents = resolve_subwords(sent, sent_surps, sent_ents)
                assert len(sent) == len(sent_surps) == len(sent_ents)
                for j, word in enumerate(sent[:-1]): # ignore eos for evaluation
                    o.write(report(word, sent_i, j, sent_surps, sent_ents))
                sent_i += 1

def score_rnn(score_fn):
    logging.info("Scoring RNN...")
    with open(score_fn, 'r') as f:
        all_scores = {}
        first = False
        score = 0.
        sent = []
        prev_sentid = -1
        for line in f:
            if line.strip() == "":
                first = True
            elif "===========================" in line:
                first = False
                break
            elif first and len(line.strip().split()) == 6 and "torch.cuda" not in line:
                wrd, sentid, wrd_score = [line.strip().split()[i] for i in [0,1,4]]
                score = -1 * float(wrd_score) # multiply by -1 to turn surps back into logprobs
                sent.append((wrd, score))
                if wrd == ".":
                    name_found = False
                    for (k1,v1) in sorted(name_lengths.items(), key=operator.itemgetter(1)):
                        if float(sentid) < v1 and not name_found:
                            name_found = True
                            if k1 not in all_scores:
                                all_scores[k1] = {}
                            key_found = False
                            for (k2,v2) in sorted(key_lengths[k1].items(), key=operator.itemgetter(1)):
                                if int(sentid) <  v2 and not key_found:
                                    key_found = True
                                    if k2 not in all_scores[k1]:
                                        all_scores[k1][k2] = []
                                    all_scores[k1][k2].append(sent)
                    sent = []
                    if float(sentid) != prev_sentid+1:
                        logging.info("Error at sents "+sentid+" and "+prev_sentid)
                    prev_sentid = float(sentid)
    return all_scores

def test_LM():
    logging.info("Testing My RNN...")
    if not os.path.exists(args.lm_output):
        os.makedirs(args.lm_output)

    test_file_list = os.listdir(args.template_dir)
    model_name = args.model.replace('/','.').split('.')[1]
    

    for output_fn in test_file_list:

        test_path = os.path.join(args.template_dir, output_fn)
        eval_path = os.path.join(args.myrnn_dir, 'test_word.py')
        
        result_fn = 'scores.txt'
        sep_tp = output_fn.replace('/','.').split('.')[0]
        lm_output_path = os.path.join(args.lm_output, model_name+'_'+sep_tp+'_'+result_fn)
        results_path = os.path.join(args.lm_output, 'results.pickle')
        
        capitalize = '--capitalize' if args.capitalize else ''
        cmd = 'python {} --data {} --model {} --output {} --ignore-eos  {}'.format(eval_path, test_path, args.model, lm_output_path, capitalize)
        print(cmd)
        os.system(cmd)

    '''
    
    logging.info("Testing My RNN...")
    test_path = os.path.join(args.template_dir, args.output_file)
    eval_path = os.path.join(args.myrnn_dir, 'test_word.py')

    result_fn = 'scores.txt'
    sep_tp = args.output_file.replace('.')[0]
    lm_output_path = os.path.join(args.lm_output, sep_tp+'_'+result_fn)
    results_path = os.path.join(args.lm_output, 'results.pickle')
    
    capitalize = '--capitalize' if args.capitalize else ''
    cmd = 'python {} --data {} --model {} --output {} --ignore-eos  {}'.format(eval_path, test_path, args.model, lm_output_path, capitalize)
    print(cmd)
    os.system(cmd)
    #args2 = [eval_path, test_path, args.model, lm_output_path, capitalize]
    #run_test(args2)
    #results = score_rnn(lm_output_path)

    '''


if __name__ == '__main__':
    test_LM()
