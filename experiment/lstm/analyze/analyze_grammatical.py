import argparse
import pickle
import os,sys
import subprocess
import operator
import logging
import csv, json
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

def write_csv(write_fn, row):
    with open(write_fn, "a") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def fn2item(fn):
    #単文
    if "test_simple_l4h0v20_unk" in fn:
        return "sim_l4h0"
    elif "test_simple_l4h1v20_unk" in fn:
        return "sim_l4h1"
    elif "test_simple_l4h2v20_unk" in fn:
        return "sim_l4h2"
    elif "test_simple_l4h3v20_unk" in fn:
        return "sim_l4h3"

    #複文
    #連用節主節
    elif "test_complex_adv_main_l4h0v20_unk" in fn:
        return "adv_main_l4h0"
    elif "test_complex_adv_main_l4h1v20_unk" in fn:
        return "adv_main_l4h1"
    elif "test_complex_adv_main_l4h2v20_unk" in fn:
        return "adv_main_l4h2"
    elif "test_complex_adv_main_l4h3v20_unk" in fn:
        return "adv_main_l4h3"
    #連用節従属節
    elif "test_complex_adv_sub_l4h0v20_unk" in fn:
        return "adv_sub_l4h0"
    elif "test_complex_adv_sub_l4h1v20_unk" in fn:
        return "adv_sub_l4h1"
    elif "test_complex_adv_sub_l4h2v20_unk" in fn:
        return "adv_sub_l4h2"
    elif "test_complex_adv_sub_l4h3v20_unk" in fn:
        return "adv_sub_l4h3"
    
    #連体節主節
    elif "test_complex_adj_main_l4h0v20_unk" in fn:
        return "adj_main_l4h0"
    elif "test_complex_adj_main_l4h1v20_unk" in fn:
        return "adj_main_l4h1"
    elif "test_complex_adj_main_l4h2v20_unk" in fn:
        return "adj_main_l4h2"
    elif "test_complex_adj_main_l4h3v20_unk" in fn:
        return "adj_main_l4h3"
    
    #連体節従属節
    elif "test_complex_adj_sub_l4h0v20_unk" in fn:
        return "adj_sub_l4h0"
    elif "test_complex_adj_sub_l4h1v20_unk" in fn:
        return "adj_sub_l4h1"
    elif "test_complex_adj_sub_l4h2v20_unk" in fn:
        return "adj_sub_l4h2"
    elif "test_complex_adj_sub_l4h3v20_unk" in fn:
        return "adj_sub_l4h3"

    #補足節主節
    elif "test_complex_sup_main_l4h0v20_unk" in fn:
        return "sup_main_l4h0"
    elif "test_complex_sup_main_l4h1v20_unk" in fn:
        return "sup_main_l4h1"
    elif "test_complex_sup_main_l4h2v20_unk" in fn:
        return "sup_main_l4h2"
    elif "test_complex_sup_main_l4h3v20_unk" in fn:
        return "sup_main_l4h3"
    
    #補足節従属節
    elif "test_complex_sup_sub_l4h0v20_unk" in fn:
        return "sup_sub_l4h0"
    elif "test_complex_sup_sub_l4h1v20_unk" in fn:
        return "sup_sub_l4h1"
    elif "test_complex_sup_sub_l4h2v20_unk" in fn:
        return "sup_sub_l4h2"
    elif "test_complex_sup_sub_l4h3v20_unk" in fn:
        return "sup_sub_l4h3"
    
    else:
        return "other"
        
def fn_pick_margin(fn):
    margin = fn.split("_")[2]
    return margin
    

if __name__ == "__main__":
    args = sys.argv
    file_name_dir = args[1]
    fn_list = os.listdir(file_name_dir)
    result_dic = {}
    for each_file_name in fn_list:
        item = fn2item(each_file_name)
        #print(each_file_name, item)
        #exit()
        file_name = os.path.join(file_name_dir,each_file_name)
        all_scores = score_rnn(file_name)
        correct_sents, incorrect_sents, success = compare_sent(all_scores)

        try:
            all_num = str(len(all_scores)/2)
            accuracy = str(success/len(all_scores)*2)
        except:
            continue
        
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
            wf.write("総数："+all_num+"\t正解数："+str(success)+"\t正解率:"+accuracy)
        
        logging.info(file_name)
        logging.info("総数："+all_num+"\t正解数："+str(success)+"\t正解率:"+accuracy)
        margin = fn_pick_margin(each_file_name)
        try:
            result_dic[margin][item] = {"all":all_num, "s_num":str(success), "acc":accuracy}
        except:
            result_dic[margin] = {}
            result_dic[margin][item] = {"all":all_num, "s_num":str(success), "acc":accuracy}
        #print(result_dic)


    item_list = ["sim_l4h0","sim_l4h1","sim_l4h2","sim_l4h3",
                 "adv_main_l4h0","adv_main_l4h1","adv_main_l4h2","adv_main_l4h3",
                 "adv_sub_l4h0","adv_sub_l4h1","adv_sub_l4h2","adv_sub_l4h3",
                 "adj_main_l4h0","adj_main_l4h1","adj_main_l4h2","adj_main_l4h3",
                 "adj_sub_l4h0","adj_sub_l4h1","adj_sub_l4h2","adj_sub_l4h3",
                 "sup_main_l4h0","sup_main_l4h1","sup_main_l4h2","sup_main_l4h3",
                 "sup_sub_l4h0","sup_sub_l4h1","sup_sub_l4h2","sup_sub_l4h3"
    ]
    write_csv_fn = "result_"+ file_name_dir.replace("/","")+".csv"
    write_csv(write_csv_fn, ["margin", "item", "all_num", "s_num", "acc"])
    for each_margin in result_dic.keys():
        write_csv(write_csv_fn, [each_margin])
        logging.info(each_margin)
        with open("result_"+file_name_dir.replace("/","")+"_"+each_margin+".json","w") as wj:
            json.dump(result_dic[each_margin],wj)
        for each_item in item_list:
            write_csv(write_csv_fn,
                      ["",
                       each_item,
                       result_dic[each_margin][each_item]["all"],
                       result_dic[each_margin][each_item]["s_num"],
                       result_dic[each_margin][each_item]["acc"]
                      ])
            logging.info(each_item)
        
