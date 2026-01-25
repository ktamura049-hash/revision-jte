import json
import io, sys, os

def get_data(dic):
    all_num = dic["all"]
    s_num = dic["s_num"]
    return int(float(all_num)), int(float(s_num))

with open(sys.argv[1])as f:
    result = json.load(f)


tan_all = 0
tan_s = 0
adj_all = 0
adj_s = 0
hei_syu_all = 0
hei_syu_s = 0
hei_ju_all = 0
hei_ju_s = 0
ren_syu_all = 0
ren_syu_s = 0
ren_ju_all = 0
ren_ju_s = 0
hosoku_syu_all = 0
hosoku_syu_s = 0
hosoku_ju_all = 0
hosoku_ju_s = 0
hosoku_setsu_all = 0
hosoku_setsu_s = 0


for each_key in result.keys():
    all_num, s_num = get_data(result[each_key])
    if "tan" in each_key:
        tan_all += all_num
        tan_s += s_num
    elif "adj" in each_key:
        adj_all += all_num
        adj_s += s_num
    elif "hei" in each_key:
        if "syu" in each_key:
            hei_syu_all += all_num
            hei_syu_s += s_num
        elif "ju" in each_key:
            hei_ju_all += all_num
            hei_ju_s += s_num
    elif "ren" in each_key:
        if "syu" in each_key:
            ren_syu_all += all_num
            ren_syu_s += s_num
        elif "ju" in each_key:
            ren_ju_all += all_num
            ren_ju_s += s_num
    elif "hosoku" in each_key:
        if "syu" in each_key:
            hosoku_syu_all += all_num
            hosoku_syu_s += s_num
        elif "ju" in each_key:
            hosoku_ju_all += all_num
            hosoku_ju_s += s_num
        elif "setsu" in each_key:
            hosoku_setsu_all += all_num
            hosoku_setsu_s += s_num

print("形容詞のない単文\t総数:", tan_all, "精度：",tan_s/tan_all)
print("形容詞のある単文\t総数:", adj_all, "精度：",adj_s/adj_all)
print("連用節の複文　主節\t総数:", hei_syu_all, "精度：",hei_syu_s/hei_syu_all)
print("連用節の複文　従属節\t総数:", hei_ju_all, "精度：",hei_ju_s/hei_ju_all)
print("連体節の複文　主節\t総数:", ren_syu_all, "精度：",ren_syu_s/ren_syu_all)
print("連体節の複文　従属節\t総数:", ren_syu_all, "精度：",ren_ju_s/ren_ju_all)
print("補足節の複文　主節\t総数:", hosoku_syu_all, "精度：",hosoku_syu_s/hosoku_syu_all)
print("補足節の複文　従属節\t総数:", hosoku_syu_all, "精度：",hosoku_ju_s/hosoku_ju_all)
print("補足節の複文　節自体\t総数:", hosoku_syu_all, "精度：",hosoku_setsu_s/hosoku_setsu_all)
