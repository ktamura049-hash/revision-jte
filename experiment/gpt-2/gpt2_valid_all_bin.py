from transformers import T5Tokenizer, AutoModelForCausalLM
import torch
import numpy as np
import tensorflow as tf
#import matplotlib as plt
import matplotlib.pyplot as plt
import sys
import io
import json

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

def scoring_sent(tokenizer, model, text):
    '''
    model = model_tokenizer[0]
    tokenizer = model_tokenizer[1]
    assert model is not None
    assert tokenizer is not None
    '''
    input_ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0)  # Batch size
    print(input_ids)
    '''
    if cuda:
        input_ids = input_ids.to('cuda')
    '''
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
    loss, logits = outputs[:2]
    sentence_prob = loss.item()
    #print("アウトプット", outputs.size())
    #print("ロジッツ",logits)
    return sentence_prob

def eval_test(tokenizer, model, path):
    
    sentences, sentences2 = read_test_data(path)

    probs = {}
    kugiri = True
    count = 0
    for j in range(len(sentences)):
        probability = 1
        cls_sentence = "[CLS]" + sentences[j]
        tokens = tokenizer.tokenize(cls_sentence)
        #print(tokens)
        '''
        for i in range(1, len(tokens)):            
            next_prob = calc_prob(tokenizer, model, ''.join(tokens[:i]), tokens[i])
            probability = probability * next_prob

            #print(tokens[:i])
            #print(tokens[i], next_prob)
        '''
        probability = scoring_sent(tokenizer, model, sentences[j])

        probs[j]={
            'pair_ID':count,
            'length':len(tokens),
            'sentence':sentences[j],
            'probability':probability,
            'hantei':kugiri
            }
                           
        print(len(tokens), sentences[j], '\t', probability)
        if not kugiri:
            print('---')
            kugiri = True
            count += 1
        else:
            kugiri = False
    for i in range(len(probs)):
        print(probs[i])
        
    return probs

def read_test_data(path):
    with io.open(path, encoding='utf-8') as f:
        text = f.read()
        #print('corpus length:', len(text))
        
        sentences = text.replace('<eos>','</s>').replace(' ','').replace('\n',' ').split()

    print('sentences = ', sentences)
        
    sentences2 = []
    with io.open(path, encoding='utf-8') as f2:
        line = f2.readline()
        countline = True
        while line:
            line = line.replace('\t','')
            line = line.replace(' ','')
            line = line.replace(' ','')
            if countline:
                line = line + '\t<true>'
                countline = False
            else :
                line = line + '\t<false>'
                countline = True
            line = line.split()
            sentences2.append(line)
            line = f2.readline()

    return sentences, sentences2



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

#for ram in range(1, len(sys.argv)):
if __name__ == '__main__':
    model_dir = sys.argv[1]
    valid_path =sys.argv[2]
    margin = sys.argv[3]
    epoch = sys.argv[4]
    # 構造的非文のvalid
    #path = "validation.txt"
    # 意味的非文のvalid
    #path = "test/imi_valid2_10k_test.txt"
    #model_dir = sys.argv[ram]
    # load tokenizer
    #model_dir = 'ft-token-margin10-'+str(ram)
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading
    
    #load model
    model = AutoModelForCausalLM.from_pretrained(model_dir,
                                                 output_hidden_states = True,
    )

    model = model.eval()
    print(model_dir)
    probs = eval_test(tokenizer, model, valid_path)
    path = valid_path.replace('.','/').split('/')[-2]
    print(path)
    save_file_name = './probs_'+model_dir.split('/')[-2]+'_margin'+margin+'_'+epoch+'_'+path+'.json'
    with open(save_file_name, mode = 'w') as sf:
        json.dump(probs, sf,ensure_ascii=False)
