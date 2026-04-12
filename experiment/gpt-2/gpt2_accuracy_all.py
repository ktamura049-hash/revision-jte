import tensorflow as tf
#import matplotlib as plt
import matplotlib.pyplot as plt
import sys
import io
import json

#from tensorflow.python.client import device_lib
#device_lib.list_local_devices()

def accuracy(probs):
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
    trueprob = truecount / count
    print('---')
    print(path)
    #print('総数:',count,'正解数:',truecount,'正解率:',trueprob)
    print('total_num:',count,'num of corrct:',truecount,'acc:',trueprob)

args = sys.argv

for i in range(1,len(args)):
    path = args[i]
    with io.open(path) as f:
        probs = json.load(f)

        #print(probs)


    #for i in range(len(probs)):
    #print(probs[str(i)]['length'])

    accuracy(probs)
