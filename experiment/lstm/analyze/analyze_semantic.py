import argparse
import pickle
import os,sys
import subprocess
import operator
import logging
from progress.bar import Bar

logging.basicConfig(level=logging.INFO)



def score_rnn(score_fn):
    logging.info("Scoring RNN...")
    with open(score_fn, 'r') as f:
        all_scores = []
        first = False
        score = 0.
        sent = ''
        prev_sentid = -1
        for line in f:
            if line.strip() == "":
                first = True
            elif "===========================" in line:
                first = False
                break
            elif first and len(line.strip().split()) == 6 and "torch.cuda" not in line:
                wrd, sentid, wrd_score = [line.strip().split()[i] for i in [0,1,4]]
                each_score = -1 * float(wrd_score) # multiply by -1 to turn surps back into logprobs
                score = score + each_score
                sent = sent + wrd
                if wrd == "。":
                    all_scores.append((sent, score))
                    sent = ''
                    score = 0.
    return all_scores

def compare_sent(all_scores):
    success = 0
    correct_sents = []
    incorrect_sents = []
    for i in range(0, len(all_scores),2):
        grammatical = all_scores[i]
        ungrammatical = all_scores[i+1]
        if grammatical[1] > ungrammatical[1]:
            correct_sents.append((grammatical,ungrammatical))
            success += 1
        else:
            incorrect_sents.append((grammatical,ungrammatical))
    return correct_sents, incorrect_sents, success

def write_result(result_list, filename):
    for result in result_list:
        grammatical, ungrammatical = result
        with open(filename, "a", encoding='utf-8') as wf:
            wf.write(str(grammatical)+"\t"+str(ungrammatical)+"\n")
            
def rm_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


if __name__ == "__main__":
    args = sys.argv
    file_name_dir = args[1]
    fn_list = os.listdir(file_name_dir)

    for each_file_name in fn_list:
        file_name = os.path.join(file_name_dir,each_file_name)
        all_scores = score_rnn(file_name)
        correct_sents, incorrect_sents, success = compare_sent(all_scores)
        write_fn = "result_"+each_file_name
        rm_file(write_fn)
        with open(write_fn, "a", encoding='utf-8') as wf:
            wf.write("正解した組\n")
        write_result(correct_sents, write_fn)
        with open(write_fn, "a", encoding='utf-8') as wf:
            wf.write("==================================================================\n\n")
            wf.write("不正解した組\n")
        write_result(incorrect_sents, write_fn)
        with open(write_fn, "a", encoding='utf-8') as wf:
            wf.write("==================================================================\n\n")
            try:
                wf.write("総数："+str(len(all_scores)/2)+"\t正解数："+str(success)+"\t正解率:"+str(success/len(all_scores)))
            except Exception as e:
                wf.write(str(e))
        
        logging.info(file_name)
        try:
            logging.info("総数："+str(len(all_scores)/2)+"\t正解数："+str(success)+"\t正解率:"+str(success/(len(all_scores)/2)))
        except Exception as e:
            logging.info(str(e))
