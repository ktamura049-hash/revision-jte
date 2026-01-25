# marge_test.py
# 正文と非文のペアを作成する

import sys,os
from cre_sent import save_sentence, remove_file


def get_lines(corpus):
    lines = []
    with open(corpus, 'r') as f:
        line = f.readline()
        while line:
            sep_line = line.split()
            #print(line[:-1])
            #print(sep_line)
            #print(sep_line[-1])
            #exit()
            if sep_line[-1] == '。':
                line = line.replace('< unk >','<unk>').replace('。','。 <eos>')
                #最後に改行が入ってるのでそこは含めない
                lines.append(line[:-1])
                
            line = f.readline()

    return lines

if __name__ == "__main__":
    file_name = sys.argv[1]
    seibun_path = "./seibun_corpus/"+file_name
    hibun_path = "./hibun_corpus/"+file_name

    w_path = "./"+file_name.split(".")[0]+"_test.txt"
    remove_file(w_path)

    seibun_list = get_lines(seibun_path)
    hibun_list = get_lines(hibun_path)

    if len(seibun_list) != len(hibun_list):
        print("正文と非文の数があってません")
        exit()

    for i in range(len(seibun_list)):
        print(i)
        print(seibun_list[i])
        save_sentence(w_path, seibun_list[i])
        print(hibun_list[i])
        save_sentence(w_path, hibun_list[i])
        
