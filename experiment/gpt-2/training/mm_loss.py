import collections
import json
import logging
import math
import os
import sys
import random
import numpy as np
import io
import datetime

import torch
import torch.nn as nn
from torch.nn import CrossEntropyLoss
from torch.nn.parameter import Parameter
import torch.nn.functional as F
from gpt2_test import convert_ids
from seihu import create_seihu_list

def SumCrossEntropyLoss(input_ids, logits):
    # Shift so that tokens < n predict n
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = input_ids[..., 1:].contiguous()
    # Flatten the tokens
    loss_fct = CrossEntropyLoss(ignore_index=-1, reduction = "sum")
    raw_loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)),
                        shift_labels.view(-1))
    return raw_loss

def TokenMarginLoss(input_ids, logits, hu_id, gold_idx, wrong_idx, n_tokens, neg_calc, targets):
    '''
    # Shift so that tokens < n predict n
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = input_ids[..., 1:].contiguous()
    # Flatten the tokens
    loss_fct = CrossEntropyLoss(ignore_index=-1, reduction = "sum")
    raw_loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)),
                        shift_labels.view(-1))
    '''
    raw_loss = SumCrossEntropyLoss(input_ids, logits)
    
    probs = F.log_softmax(logits,dim=-1)
    #print(probs)
    #print(probs.size())
    #ここで正の単語と非の単語の確率を計算
    gold_probs = []
    wrong_probs = []
    gold_one_hot = torch.zeros(probs.shape)
    wrong_one_hot = torch.zeros(probs.shape)
    for i in range(len(probs)):
        if type(hu_id[i])  == list:
            for each_id in hu_id[i]:
                gold_one_hot[i][each_id][gold_idx[i]] = 1.
                wrong_one_hot[i][each_id][wrong_idx[i]] = 1.
        else:
            gold_one_hot[i][hu_id[i]][gold_idx[i]] = 1.
            wrong_one_hot[i][hu_id[i]][wrong_idx[i]] = 1.
    gold_probs = torch.sum(torch.sum(torch.mul(probs,gold_one_hot),1),1)
    wrong_probs = torch.sum(torch.sum(torch.mul(probs,wrong_one_hot),1),1)
    #print('gold_probs',gold_probs)
    #print('wrong_probs',wrong_probs)
    gold_probs = torch.reshape(gold_probs, (-1,1))
    wrong_probs = torch.reshape(wrong_probs, (-1,1))
    #print('gold_probs',gold_probs, gold_probs.size())
    #print('wrong_probs',wrong_probs, wrong_probs.size()
    
    prob = torch.cat((gold_probs, wrong_probs),1)
    
    #prob = torch.tensor(prob).to(device)
    #print('prob',prob,prob.size())
    margin_targets = targets.new_zeros(prob.size(0))
    #print('margin_targets',margin_targets)
    neg_loss = neg_calc(prob, margin_targets) * 2.0
    #print('neg_loss',neg_loss)
    neg_loss = neg_loss.sum()
    #print('neg_loss.sum()',neg_loss)
    #print("raw_loss:",raw_loss,"\tneg_loss", neg_loss)
    loss = (raw_loss + neg_loss) /n_tokens

    return raw_loss, neg_loss, loss


