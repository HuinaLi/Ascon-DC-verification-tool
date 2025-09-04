from diff_ddt_suit import *
from sum import *
import math

def extract_hex_lists_from_file(file_path):
    hex_lists = {"B": [], "A": []}  # 用于存储B和A的16进制列表
    current_list = None  # 当前处理的是B还是A

    # 打开文件并读取内容
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # 按行处理文件内容
    for line in lines:
        line = line.strip()  # 去除行首尾空白字符
        if line.startswith('B['):  # 检测到B的开始
            current_list = "B"
            hex_lists[current_list].append([])  # 创建新列表以存储该部分的16进制数
        elif line.startswith('A['):  # 检测到A的开始
            current_list = "A"
            hex_lists[current_list].append([])  # 创建新列表以存储该部分的16进制数
        elif line.startswith('0x'):  # 如果是以0x开头的16进制数
            # 将16进制字符串转换为整数并加入列表
            hex_value = int(line, 16)
            # 将整数转换为长度为16位的16进制字符串并添加到列表中
            formatted_hex = f"0x{hex_value:016x}"
            hex_lists[current_list][-1].append(formatted_hex)

    # 返回A和B列表（整数形式的16进制数）
    return hex_lists['B'], hex_lists['A']


def ddt_intlist2binlistWithWeight(inlist:list, S_box_size:int=32) -> list:
    binlist = []
    for l in inlist:
        diff_in = [int(x) for x in int2bin(l[0], 5)]
        diff_out = [int(x) for x in int2bin(l[1], 5)]
        tmp = diff_in + diff_out + [l[2]]
        binlist.append(tmp)
    return binlist



## weight = 2* AS(B0) + w(A1) + w(A2) + w(A3)

def compute_wA1A2(B_bit_lists,A_bit_lists,relationDiffInOut):
    # pattern[0]: store the number of AS with weight 2.
    # pattern[1]: store the number of AS with weight 3.
    # pattern[2]: store the number of AS with weight 4.
    pattern=[0,0,0]
    for r in range(ROUND-2):
        for x in range(64):
            pair = [A_bit_lists[r][index_xy(x,i)] for i in range(5)] + [B_bit_lists[r+1][index_xy(x,i)] for i in range(5)]
            for vaildiff in relationDiffInOut:
                if pair == vaildiff[:10] and pair != [0 for _ in range(10)]:
                    n = vaildiff[10]
                    N = int(math.log(32//n, 2))
                    pattern[N-2] += 1
                else:
                    continue
    wA12 = 2*pattern[0] + 3*pattern[1] + 4*pattern[2]
    # print(pattern)
    return wA12


def compute_wA3(A_bit_lists):
    # pattern[0]: store the number of AS with weight 2.
    # pattern[1]: store the number of AS with weight 3.
    # pattern[2]: store the number of AS with weight 4.
    pattern=[0,0,0]
    for x in range(64):
        pair = [A_bit_lists[-1][index_xy(x,i)] for i in range(5)]
        if pair == [0,1,1,0,0]:
            pattern[0] += 1
        if pair == [1,1,0,0,1] or pair == [0,0,0,1,1] or pair == [1,1,1,0,0] or pair == [1,1,1,0,1]:
            pattern[1] += 1
        if pair == [1,0,0,1,0] or pair == [0,1,0,0,1] or pair == [0,1,1,0,1] or pair == [1,0,1,1,0]:
            pattern[2] += 1
        else:
            continue
    wA3 = 2*pattern[0] + 3*pattern[1] + 4*pattern[2]
    print(pattern)
    return wA3
            
def from_dclog_compute_weight(file_path, B_list,A_list):
    B_list, A_list = extract_hex_lists_from_file(file_path)

    print(B_list)
    print(A_list)
    
    B_bit_lists = convert_diff_to_bit_list(B_list)
    A_bit_lists = convert_diff_to_bit_list(A_list)
    
    wA12 = compute_wA1A2(B_bit_lists,A_bit_lists,relationDiffInOut)
    wA3 = compute_wA3(A_bit_lists)
    
    print(6+ wA12 + wA3)

def generate_support_verifymodelpy_dclist(file_path):
    # 使用函数提取数据
    B_list, A_list = extract_hex_lists_from_file(file_path)

    ## get A0 from Blist[0]
    bin_a0, hex_a0 = compute_as_number(B_list[0])

    Diff = []
    Diff.append(hex_a0)
    for i in  range(len(B_list)):
        Diff.append(B_list[i])
        Diff.append(A_list[i])

    bin_last,hex_blast = compute_as_number(A_list[-1])
    Diff.append(hex_blast)
    diff_bit_lists = convert_diff_to_bit_list(Diff)
    
    return diff_bit_lists


if __name__ == '__main__':
    ROUND = 5
    inlist = VaildDiffInOutWithWeight(AsconSbox)
    relationDiffInOut = ddt_intlist2binlistWithWeight(inlist)
    # print(patterns)
    # 文件路径
    file_path = '/home/user/lhn/fast_verify_new_model/code/checkdcinf.log'
    diff_bit_lists = generate_support_verifymodelpy_dclist(file_path)
    print(len( diff_bit_lists))
    
    