from transformers import T5Tokenizer, AutoModelForCausalLM
import torch
import numpy as np
import tensorflow as tf
#import matplotlib as plt
import matplotlib.pyplot as plt
import sys
import io

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

def eval_test(tokenizer, model, path):
    
    texts, texts2 = read_test_data(path)

    sentences = []
    next_chars = []
    sentbegin = set([0])

    for i in range(0, len(texts)-1):
        if texts[i] == '<eos>':
            sentbegin.add(i + 1)
                 
    sentbegin = sorted(list(sentbegin))
    probs = []
    for i in range(0, len(sentbegin)):
        probability = 1
        sentense = []
        for j in range(1000):
            text = "".join(sentense)
            cls_text = "[CLS]" + text
            next_word = texts[sentbegin[i]+j]
            next_prob = calc_prob(tokenizer, model, cls_text, next_word)
            
            #print(text)
            #print(next_word, next_prob)
            
            sentense.append(next_word)
            probability = probability * next_prob

            if '<eos>' in next_word:
                break
        text = "".join(sentense)
        print(text, '\t', probability)
        probs.append((i, probability))
        if i % 2 == 1:
            print('---')

    count = 0
    truecount = 0
    for i in range(0, len(probs), 2):
        l = probs[i:i+2]
        key_func = lambda n : n[1]
        maxprob = max(l,key = key_func)
        print(texts2[maxprob[0]])
        count += 1
        if texts2[maxprob[0]][1] == '<true>':
            truecount += 1
    trueprob = truecount / count
    print('---')
    print(path)
    print('総数:',count,'正解数:',truecount,'正解率:',trueprob)
                
                

def read_test_data(path):
    with io.open(path, encoding='utf-8') as f:
        text = f.read()
        #print('corpus length:', len(text))
        
        texts = text.replace('\n',' ').split()
        
    texts2 = []
    with io.open(path, encoding='utf-8') as f2:
        line = f2.readline()
        countline = 0
        while line:
            line = line.replace('\t','')
            line = line.replace(' ','')
            line = line.replace(' ','')
            if countline == 0:
                line = line + '\t<true>'
                countline = 1
            else :
                line = line + '\t<false>'
                countline = 0
            line = line.split()
            texts2.append(line)
            line = f2.readline()

    return texts, texts2



def calc_prob(tokenizer, model, text, next_word):

    #text = "[CLS]" + text

    token_tensor, position_id_tensor, num_tokens = convert_tensor(tokenizer, text)

    #始点と終点
    start_id = 0
    end_id = num_tokens - 1
    
    with torch.no_grad():
        outputs = model(input_ids=token_tensor, position_ids=position_id_tensor)
        #確率分布
        predictions = outputs[0][start_id, end_id]
        #predictions_sort
        
        hidden_states = outputs[2]
        
    x_numpy = outputs[0][start_id, end_id].numpy()

    prob = softmax(x_numpy)
    
    # convert to ids
    #print(next_word)
    token_ids = tokenizer.convert_tokens_to_ids(next_word)
    #token = tokenizer.convert_ids_to_tokens([token_ids])[0]
    #print(next_word, token_ids, token, prob[token_ids])

    next_prob = prob[token_ids]

    return next_prob
        

def convert_ids(tokenizer, text):
    # tokenize
    tokens = tokenizer.tokenize(text)
    #print(tokens)  # output: ['[CLS]', '_4', '年に', '1', '度', 'オリンピック', 'は', '開かれる', '。']']
    
    
    # convert to ids
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    #print(token_ids)  # output: [4, 1602, 44, 24, 368, 6, 11, 21583, 8]

    return tokens, token_ids

def convert_tensor(tokenizer, text):
    #ids
    tokens, token_ids = convert_ids(tokenizer, text)
    
    # convert to tensor
    token_tensor = torch.LongTensor([token_ids])
    #print(token_tensor)

    # provide position ids explicitly
    position_ids = list(range(0, token_tensor.size(1)))
    #print(position_ids)  # output: [0, 1, 2, 3, 4, 5, 6, 7, 8]
    position_id_tensor = torch.LongTensor([position_ids])

    return token_tensor, position_id_tensor, len(tokens)

def softmax(x):

        max = np.max(x,axis=0,keepdims=True) #returns max of each row and keeps same dims
        e_x = np.exp(x - max) #subtracts each row with its max value
        sum = np.sum(e_x,axis=0,keepdims=True) #returns sum of each row and keeps same dims
        f_x = e_x / sum
        return f_x
'''
    
# main


'''

if __name__ == "__main__":
    #model_size = "medium"
    model_size = "xsmall"
    # load tokenizer
    tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-gpt2-"+model_size)
    tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading

    #load model
    model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-"+model_size,
                                                 output_hidden_states = True,
    )

    model = model.eval()

    for ram in range(1, len(sys.argv)):
        path = sys.argv[ram]
        print(path)
        eval_test(tokenizer, model, path)
