# result_seiri.py

# gpt2で得たテスト結果のテキストファイルから、各項目の総数、正解数、精度をまとめたCSVファイルを作成する

import csv
import os, sys

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
    

def rm_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

def write_csv(write_fn, row):
    with open(write_fn, "a", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(row)


if __name__ == "__main__":
    text_fn = sys.argv[1]
    result_dic = {}
    with open(text_fn, 'r') as f:
        lines = f.readlines()

    for line in lines:
        # 項目名を取得し保存
        if "json" in line:
            item = fn2item(line)
        # ペアの総数、正解数、精度をresult_dicに記録
        elif "総数" in line:
            s_line = line.split()
            all_num = s_line[1]
            s_num = s_line[3]
            accuracy = s_line[5]
            
            result_dic[item] = {"all":all_num, "s_num":s_num, "acc":accuracy}
    # 項目のリスト
    item_list = ["sim_l4h0","sim_l4h1","sim_l4h2","sim_l4h3",
                 "adv_main_l4h0","adv_main_l4h1","adv_main_l4h2","adv_main_l4h3",
                 "adv_sub_l4h0","adv_sub_l4h1","adv_sub_l4h2","adv_sub_l4h3",
                 "adj_main_l4h0","adj_main_l4h1","adj_main_l4h2","adj_main_l4h3",
                 "adj_sub_l4h0","adj_sub_l4h1","adj_sub_l4h2","adj_sub_l4h3",
                 "sup_main_l4h0","sup_main_l4h1","sup_main_l4h2","sup_main_l4h3",
                 "sup_sub_l4h0","sup_sub_l4h1","sup_sub_l4h2","sup_sub_l4h3"
    ]
    save_fn = "result_"+ text_fn.replace("/",".").split(".")[0]+".csv"
    write_csv(save_fn, [ "item", "all_num", "s_num", "acc"])
    # 各項目順に保存
    print(result_dic)
    print(save_fn)
    for each_item in item_list:
        write_csv(save_fn,
                  [
                  each_item,
                  result_dic[each_item]["all"],
                  result_dic[each_item]["s_num"],
                  result_dic[each_item]["acc"]
                  ])
