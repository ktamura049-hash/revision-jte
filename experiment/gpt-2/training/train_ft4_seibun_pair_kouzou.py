import copy
import random
import numpy as np
import io
import sys
import datetime

import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#device = torch.device("cuda")
import torch.nn as nn
import torch.nn.functional as F
from gpt2_test import convert_ids
from seihu import create_seihu_list

from mm_loss import *

#今回チューニングする事前学習済みのGPT-2
from transformers import T5Tokenizer, AutoModelForCausalLM

pretraining_path  = "rinna/japanese-gpt2-medium"

gpt_tokenizer = T5Tokenizer.from_pretrained(pretraining_path)
gpt = AutoModelForCausalLM.from_pretrained(pretraining_path).to(device)
gpt_optimizer = torch.optim.Adam(gpt.parameters(),lr=1e-4)

from torchinfo import summary
from torchvision.models import resnet18

summary(gpt)
#exit()

train_corpus = 'train2_100k.txt'
#学習コーパス（非文コーパス）
#train_corpus = 'not-unk_train2_100k.txt'

#学習コーパス（非文コーパス）
# 構造的非文を学習させるとき
train_data_path = './hibun_' + train_corpus
# 意味的非文を学習させるとき
#train_data_path = './imihibun_train2_100k.txt'

#正文コーパス
gold_path = train_corpus

#行を一致させるための非文コーパス
# 構造的非文を学習させるとき
wrong_path = './none_' + train_corpus
# 意味的非文を学習させるとき
#wrong_path = './none_imihibun_train2_100k.txt'

#保存ファイル
save_file_name = "train-ft4_seibun_kouzou_pair" + pretraining_path.split("/")[-1] + train_data_path.replace("/","").split(".")[-2]

#
#save_file_name += '_imi'

BOS_IDX = gpt_tokenizer.bos_token_id
EOS_IDX = gpt_tokenizer.eos_token_id
PAD_IDX = gpt_tokenizer.pad_token_id
UNK_IDX = gpt_tokenizer.unk_token_id
print(UNK_IDX, gpt_tokenizer.convert_ids_to_tokens(UNK_IDX))
VOCAB_SIZE = gpt_tokenizer.vocab_size
#exit()
#負例の格助詞の判定「$」のインデックス
HU_IDX = gpt_tokenizer.convert_tokens_to_ids('$')
#print(HU_IDX, gpt_tokenizer.convert_ids_to_tokens(HU_IDX))

SEQ_LEN = 30
BATCH_SIZE = 256
EPOCH_SIZE = 10
if len(sys.argv) > 1:
    penalty = float(sys.argv[1])
else:
    penalty = 1

save_file_name = save_file_name + "_pe" + str(penalty)
w_path = "./"+save_file_name+".txt"

class hurei_loss(nn.Module):
    def __init__(self):
        super(hurei_loss, self).__init__()

    def forward(self, probs, targets,margin):
        targets_onehot = F.one_hot(targets, num_classes = VOCAB_SIZE)
        #targets_onehot2 = F.one_hot(targets2, num_classes = VOCAB_SIZE)
        #targets = targets_onehot+targets_onehot2*margin
        #print(torch.log(probs).size())
        #print(targets_onehot.size())
        loss = -(torch.log(probs)*targets).sum(-1)
        #print(loss)
        return loss.mean()

def create_neg_sample(samples, hu_id, sentence, gold_word, gold_idx, wrong_idx, s_lens):
    # "$"がついている状態で一度トークン化する
    tokens, token_ids = convert_ids(gpt_tokenizer, sentence)
    # "$"を消す
    sentence2 = sentence.replace('$','')
    # "$"を消した状態でもう一度トークン化する
    tokens2, token_ids2 = convert_ids(gpt_tokenizer, sentence2)
    # "$"を消した状態と、消さなかった状態で、tokenizerの区切りが変わってしまったら
    #print('token_ids',set(token_ids))
    #print(set(token_ids2+[HU_IDX]))
    if set(token_ids) != set(token_ids2+[HU_IDX]):
        #処理を終了。追加はしない
        return samples, hu_id, gold_idx, wrong_idx, s_lens

    if len(token_ids2) > 29 :
        return samples, hu_id, gold_idx, wrong_idx, s_lens

    # "$"の出た位置を記録
    for  i in range(len(token_ids)):
        if token_ids[i] == HU_IDX:
            #print(i, token_ids2[i])
            hu_id.append(i)
            wrong_word = copy.deepcopy(token_ids2[i])
            wrong_idx.append(wrong_word)
            gold_idx.append(gold_word)
            token_ids2[i] = copy.deepcopy(gold_word)
            s_len = len(token_ids2)
            s_lens.append(s_len)

    #前後にBOSとEOSを追加
    #token_ids =  [BOS_IDX]+token_ids+[EOS_IDX]
    token_ids2 =  [BOS_IDX]+token_ids2+[EOS_IDX]
    #パディングする
    while True:
        if len(token_ids2) > SEQ_LEN:
            break
        token_ids2 = token_ids2 + [PAD_IDX]
    #print(token_ids2)
    
    samples.append(token_ids2)
    
    return samples, hu_id, gold_idx, wrong_idx, s_lens

def create_gold_sample(samples, sentence, s_lens):
    # トークン化する
    tokens, token_ids = convert_ids(gpt_tokenizer, sentence)
    s_len = len(token_ids)
    if s_len > 29 :
        return samples, s_lens
    
    s_lens.append(s_len)
    
    #前後にBOSとEOSを追加
    token_ids =  [BOS_IDX]+token_ids+[EOS_IDX]
    #パディングする
    while True:
        if len(token_ids) > SEQ_LEN:
            break
        token_ids = token_ids + [PAD_IDX]
        #print(token_ids)
    samples.append(token_ids)
    
    return samples, s_lens

def read_train_data(path):
    with io.open(path, encoding='utf-8') as f:
        text = f.read()
        #print('corpus length:', len(text))
        
    sentences = text.replace(' ','').replace('　','').replace('\t',' ').split()
    #print('sentences = ', sentences)
    
    return sentences

def write_sentence(path, sentence):
    with io.open(path, mode='a', encoding='utf-8') as f2:
        f2.write(sentence+'\n')

def write_loss(path, loss, epoch):
    now = datetime.datetime.now()
    strnow = now.strftime('%Y-%m-%d %H:%M:%S')
    sentence = 'epoch:'+str(epoch)+'\tloss:'+str(loss)+'\t'+strnow
    write_sentence(path, sentence)
        
hu_loss = hurei_loss()

gold_samples = []
neg_samples = []
hu_id = []
gold_idx = []
wrong_idx = []
gold_s_lens = []
neg_s_lens = []

_, gold_words, _ = create_seihu_list(gold_path,wrong_path)
#print(gold_words)

# 正文のみの学習データの作成
gold_sentences = read_train_data(gold_path)
for gold_sentence in gold_sentences:
    gold_samples,  gold_s_lens = create_gold_sample(gold_samples, gold_sentence, gold_s_lens)

# 正文と非文の学習データの作成
neg_sentences = read_train_data(train_data_path)
for i, neg_sentence in enumerate(neg_sentences):
    gold_word = gpt_tokenizer.convert_tokens_to_ids(gold_words[i])
    neg_samples, hu_id, gold_idx, wrong_idx, neg_s_lens = create_neg_sample(neg_samples, hu_id, neg_sentence, gold_word, gold_idx, wrong_idx, neg_s_lens)

if len(gold_idx) != len(wrong_idx):
    print('goldとwrongの数があってません')
    exit()

if len(neg_samples) != len(hu_id):
    print("error")
    exit()


if len(gold_samples + neg_samples) < 20:
    print('gold_samples',gold_samples)
    print('neg_samples',neg_samples)
    print('hu_id:',hu_id)
    print('gold_idx:',gold_idx)
    print('wrong_idx:',wrong_idx)

'''
for i in range(1):
    print('samples',i,samples[i])
print(sentences[:1])
print('hu_id:',hu_id[:19])
print('gold_idx2:',gold_idx[:10])
print('wrong_idx:',wrong_idx[:10])
'''
print('が:',gpt_tokenizer.convert_tokens_to_ids('が'))
print('を:',gpt_tokenizer.convert_tokens_to_ids('を'))
print('に:',gpt_tokenizer.convert_tokens_to_ids('に'))
print('へ:',gpt_tokenizer.convert_tokens_to_ids('へ'))
print('と:',gpt_tokenizer.convert_tokens_to_ids('と'))
print('で:',gpt_tokenizer.convert_tokens_to_ids('で'))
print('から:',gpt_tokenizer.convert_tokens_to_ids('から'))
print('まで:',gpt_tokenizer.convert_tokens_to_ids('まで'))
print('より:',gpt_tokenizer.convert_tokens_to_ids('より'))
print('の:',gpt_tokenizer.convert_tokens_to_ids('の'))
#exit()    
''' 
sentence = '私は山形大学$を行く。'
samples, hu_id = create_sample(samples, hu_id, sentence)

sentence = '私は山形大学$より行く。'
samples, hu_id = create_sample(samples, hu_id, sentence)

sentence = '彼は頂上$より目指している。'
samples, hu_id = create_sample(samples, hu_id, sentence)
'''

gold_samples = torch.tensor(gold_samples).to(device)
neg_samples = torch.tensor(neg_samples).to(device)

#for i in range(len(samples)):
    #print(gpt_tokenizer.convert_ids_to_tokens(samples[i]))

if BATCH_SIZE > len(gold_samples):
    gold_num_batch = 1
else:
    gold_num_batch = int(len(gold_samples) / BATCH_SIZE)
    
if BATCH_SIZE > len(neg_samples):
    neg_num_batch = 1
else:
    neg_num_batch = int(len(neg_samples) / BATCH_SIZE)

neg_calc = torch.nn.MultiMarginLoss(margin=penalty, reduction='none')

for epoch in range(EPOCH_SIZE):
    '''
    for iter in range(gold_num_batch):
        sample = gold_samples[iter*BATCH_SIZE:min((iter+1)*BATCH_SIZE, len(gold_samples))]
        n_tokens = sum(gold_s_lens[iter*BATCH_SIZE:min((iter+1)*BATCH_SIZE, len(gold_s_lens))])
        #print(type(samples))
        sample = torch.tensor(sample).to(device)
        targets = sample[:,1:]
        #print('targets.size:', targets.size())
        #print(type(targets))
        
        #input作成部
        samples_pad = sample
        #print('samples_pad',samples_pad[:,:-1])
        attention_mask = torch.ones(samples_pad.shape).to(device)
        gpt_optimizer.zero_grad()
        logits = gpt(input_ids=samples_pad[:,:-1],attention_mask=attention_mask[:,:-1]).logits

        raw_loss = SumCrossEntropyLoss(samples_pad[:,:-1], logits)
        loss = raw_loss  / n_tokens
        if iter % 5 == 0 :
            print(iter+1, '/', neg_num_batch)
            print("gold_loss", loss)

        loss.backward()
        gpt_optimizer.step()
        
    '''
    for iter in range(neg_num_batch):
        sample = neg_samples[iter*BATCH_SIZE:min((iter+1)*BATCH_SIZE, len(neg_samples))]
        n_tokens = sum(neg_s_lens[iter*BATCH_SIZE:min((iter+1)*BATCH_SIZE, len(neg_s_lens))])
        #print(type(samples))
        sample = torch.tensor(sample).to(device)
        targets = sample[:,1:]
        #print('targets.size:', targets.size())
        #print(type(targets))

        #input作成部
        samples_pad = sample
        #print('samples_pad',samples_pad[:,:-1])
        attention_mask = torch.ones(samples_pad.shape).to(device)
        gpt_optimizer.zero_grad()
        logits = gpt(input_ids=samples_pad[:,:-1],attention_mask=attention_mask[:,:-1]).logits

        raw_loss = SumCrossEntropyLoss(samples_pad[:,:-1], logits)
        loss = raw_loss  / n_tokens
        #raw_loss, neg_loss, loss = TokenMarginLoss(samples_pad[:,:-1], logits, hu_id, gold_idx, wrong_idx, n_tokens, neg_calc, targets)
        #print("raw_loss,", raw_loss, "neg_loss,", neg_loss,"loss", loss)
        if iter % 5 == 0 :
            print(iter+1, '/', neg_num_batch)
            print("gold_loss", loss)

        loss.backward()
        gpt_optimizer.step()
     
        
    #exit()
            
    torch.save(gpt.state_dict(),"./"+save_file_name+"_"+str(epoch)+".bin")
    print("save epoch", epoch)
    write_loss(w_path,loss, epoch)
