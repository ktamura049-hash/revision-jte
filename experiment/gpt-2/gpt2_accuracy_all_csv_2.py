import tensorflow as tf
#import matplotlib as plt
import matplotlib.pyplot as plt
import sys, os
import io
import json
import csv

#from tensorflow.python.client import device_lib
#device_lib.list_local_devices()


    
def accuracy(probs):
    true_pair = []
    false_pair = []
    
    count = 0
    truecount = 0
    
    for i in range(0,len(probs),2):
        l = [probs[str(i)],probs[str(i+1)]]
        '''
        if probs[str(i)]['length'] != probs[str(i+1)]['length'] or probs[str(i)]['pair_ID'] != probs[str(i+1)]['pair_ID']:
            continue
        '''
        key_func = lambda n : n['probability']
        maxprob = min(l,key = key_func)
        #print(probs[str(i)],'\n',probs[str(i+1)])
        print(maxprob)
        #print(maxprob['sentence'])
        count += 1
        #print(type(maxprob['hantei']))
        if maxprob['hantei']:
            truecount += 1
            true_pair.append((probs[str(i)]['sentence'],probs[str(i+1)]['sentence'],'正文'))
        else:
            false_pair.append((probs[str(i)]['sentence'],probs[str(i+1)]['sentence'],'非文'))
    trueprob = truecount / count
    print('---')
    print(path)
    #print('総数:',count,'正解数:',truecount,'正解率:',trueprob)
    print('total_num:',count,'num of corrct:',truecount,'acc:',trueprob)


    return true_pair, false_pair

def write_csv(write_path, each_column):
    with open(write_path, 'a',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(each_column)

def delete_file(write_path):
    if os.path.exists(write_path):
        os.remove(write_path)

if __name__ == '__main__':
    args = sys.argv
    for i in range(1,len(args)):
        path = args[i]
        with io.open(path) as f:
            probs = json.load(f)

            #print(probs)

        #for i in range(len(probs)):
        #print(probs[str(i)]['length'])
        
        true_pair, false_pair = accuracy(probs)
        write_path = path[:-4]+'csv'
        delete_file(write_path)
        #write_csv(write_path, write_path)
        write_csv(write_path, ['不正解のリスト'])
        for each_column in false_pair:
            write_csv(write_path, each_column)
        write_csv(write_path, '')
        write_csv(write_path, ['正解のリスト'])
        for each_column in true_pair:
            write_csv(write_path, each_column)

        print(write_path,'に保存しました。')
