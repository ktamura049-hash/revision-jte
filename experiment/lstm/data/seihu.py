import sys, io

def create_seihu_list(path1, path2):
    hu_id = []
    gold_word = []
    wrong_word = []

    with io.open(path1, encoding='utf-8') as f1:
        gold_lines = f1.readlines()
    with io.open(path2, encoding='utf-8') as f2:
        wrong_lines = f2.readlines()

    #print('gold_lines:',gold_lines)
    #print('wrong_lines:',wrong_lines)

    for i in range(len(gold_lines)):
        print_sentence = str(i) + " "
        gold_words = gold_lines[i].replace('\n','').split()
        #print('gold_words', gold_words)
        
        wrong_line = wrong_lines[i].replace("< unk >","<unk>").replace('\t\n','\n').split('\t')
        #print('wrong_line', wrong_line)
            
        for j in range(len(wrong_line)):
            wrong_words = wrong_line[j].replace('\n','<eos>').split()
            #print('wrong_words', wrong_words)

            for k in range(len(wrong_words)):
                if '$' in wrong_words[k]:
                    #if i < 100:
                        #print(gold_words)
                        #print(wrong_words)
                    hu_id.append(k)
                    gold_word.append(gold_words[k])
                    wrong_word.append(wrong_words[k][1:])
                    print_sentence = print_sentence +str(k)+" "+str(wrong_words[k][1:])+" True"+"\t"
        print(print_sentence)


    return hu_id, gold_word, wrong_word

if __name__ == '__main__':
    args = sys.argv
    path1 = args[1]
    path2 = args[2]

    hu_id, gold_idx, wrong_idx = create_seihu_list(path1,path2)

    #print('hu_id', hu_id[:10],'\nlen:',len(hu_id))
    #print('gold_word', gold_idx[:10],'\nlen:',len(gold_idx))
    #print('wrong_word', wrong_idx[:10],'\nlen:',len(wrong_idx))
