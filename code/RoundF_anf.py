from sage.all import *
from sage.rings.polynomial.pbori import *
import logging

# create logger
logger = logging.getLogger('RoundF_in_ANF_form')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('c:%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def SingleMatrix(R, X, r0, r1):
    """SingleMatrix transform X

    Args:
        X (list): 64 bit input
        r0 (int): shift bits r0
        r1 (int): shift bits r1

    Returns:
        list: 64 bit output
    """
    Y = []
    for i in range(64):
        # the SingleMatrix transform
        Y.append(X[i] + X[(i + (64 - r0)) % 64] + X[(i + (64 - r1)) % 64])
    return Y

def InvSingleMatrix(X, r0, r1):
    """Inverse of the SingleMatrix transform

    Args:
        X (list): 64 bit input
        r0 (int): shift bits r0
        r1 (int): shift bits r1

    Returns:
        list: 64 bit output
    """
    # convert X to sage matrix(use self defined ring)
    tempX = matrix(R, 1, 64, X)
    tempX = tempX.transpose()
    # convert SingleMatrix to sage matrix(use GF2 ring)
    m = matrix(GF(2), 64, 64)  # a 64*64 matrix with all zeroes
    # construct the matrix
    for i in range(64):
        temp = [0] * 64
        # set the i th, i-r0 th, i-r1 th bits to 1
        temp[i], temp[(i - r0) % 64], temp[(i - r1) % 64] = 1, 1, 1
        m[i] = temp
    # compute inverse of SingleMatrix
    m = m.inverse()
    # compute output after inverse of SingleMatrix
    Y = m * tempX
    # convert sage matrix to python list
    return Y.list()

def Matrix(X):
    """Matrix transform

    Args:
        X (list): 320 bit input

    Returns:
        list: 320 bit output
    """
    # 64 bits as a block, each block uses different transform shift r0, r1
    X[0  : 64] = SingleMatrix(R, X[0  : 64], 19, 28)
    X[64 :128] = SingleMatrix(R, X[64 :128], 61, 39)
    X[128:192] = SingleMatrix(R, X[128:192], 1, 6)
    X[192:256] = SingleMatrix(R, X[192:256], 10, 17)
    X[256:320] = SingleMatrix(R, X[256:320], 7, 41)
    return X
    
def InvMatrix(X):
    """Inverse of the Matrix transform

    Args:
        X (list): 320 bit input

    Returns:
        list: 320 bit output
    """
    X[0  : 64] = InvSingleMatrix(X[0  : 64], 19, 28)
    X[64 :128] = InvSingleMatrix(X[64 :128], 61, 39)
    X[128:192] = InvSingleMatrix(X[128:192], 1, 6)
    X[192:256] = InvSingleMatrix(X[192:256], 10, 17)
    X[256:320] = InvSingleMatrix(X[256:320], 7, 41)
    return X

def SingleSbox(y0, y1, y2, y3, y4):
    """5-bits sbox

    Args:
        y0 (int): 1 bit input, 0 or 1
        y1 (int): 1 bit input, 0 or 1
        y2 (int): 1 bit input, 0 or 1
        y3 (int): 1 bit input, 0 or 1
        y4 (int): 1 bit input, 0 or 1

    Returns:
        list: 5 bits output
    """
    x0 = y4*y1 + y3 + y2*y1 + y2 + y1*y0 + y1 + y0
    x1 = y4 + y3*y2 + y3*y1 + y3 + y2*y1 + y2 + y1 + y0
    x2 = y4*y3 + y4 + y2 + y1 + 1
    x3 = y4*y0 + y4 + y3*y0 + y3 + y2 + y1 + y0
    x4 = y4*y1 + y4 + y3 + y1*y0 + y1
    return x0, x1, x2, x3, x4

def InvSingleSbox(y0, y1, y2, y3, y4):
    """inverse of the 5-bits sbox

    Args:
        y0 (int): 1 bit input, 0 or 1
        y1 (int): 1 bit input, 0 or 1
        y2 (int): 1 bit input, 0 or 1
        y3 (int): 1 bit input, 0 or 1
        y4 (int): 1 bit input, 0 or 1

    Returns:
        list: 5 bits output
    """
    x0 = y4*y3*y2 + y4*y3*y1 + y4*y3*y0 + y3*y2*y0 + y3*y2 + y3 + y2 + y1*y0 + y1 + 1
    x1 = y4*y2*y0 + y4 + y3*y2 + y2*y0 + y1 + y0
    x2 = y4*y3*y1 + y4*y3 + y4*y2*y1 + y4*y2 + y3*y1*y0 + y3*y1 + y2*y1*y0 + y2*y1 + y2 + 1 + x1
    x3 = y4*y2*y1 + y4*y2*y0 + y4*y2 + y4*y1 + y4 + y3 + y2*y1 + y2*y0 + y1
    x4 = y4*y3*y2 + y4*y2*y1 + y4*y2*y0 + y4*y2 + y3*y2*y0 + y3*y2 + y3 + y2*y1 + y2*y0 + y1*y0
    return x0, x1, x2, x3, x4

def Sbox(Y):
    """320 bits sbox

    Args:
        Y (list): 320 bits input

    Returns:
        list: 320 bits output
    """
    Z = [R(0) for i in range(320)]
    # 5 bits as a block, each block uses a 5-bits sbox
    for j in range(64):
        Z[0 + j], Z[64 + j], Z[128 + j], Z[192 + j] , Z[256 + j] = SingleSbox(Y[0 + j], Y[64 + j], Y[128 + j], Y[192 + j], Y[256+j])
    return Z

def InvSbox(Y):
    """inverse of the 320 bits sbox

    Args:
        Y (list): 320 bits input

    Returns:
        list: 320 bits output
    """
    Z = [R(0) for i in range(320)]
    # 5 bits as a block, each block uses a 5-bits sbox
    for j in range(64):
        Z[0 + j], Z[64 + j], Z[128 + j], Z[192 + j] , Z[256 + j] = InvSingleSbox(Y[0 + j], Y[64 + j], Y[128 + j], Y[192 + j], Y[256+j])
    return Z

def addConst(X, r):
    """add a const to input X

    Args:
        X (list): 320 bits input
        r (int): const index

    Returns:
        list: 320 bits output
    """
    # the chosen list of the consts
    constant = [0xf0, 0xe1, 0xd2, 0xc3, 0xb4, 0xa5, 0x96, 0x87, 0x78, 0x69,
            0x5a, 0x4b]
    base = 184
    for i in range(8):
        # choose the const according to the index r
        if constant[r] >> (7 - i) & 0x1:
            X[base + i] += 1
    return X

def round(X, r):
    """round function

    Args:
        X (list): 320 bits input
        r (int): the number of rounds

    Returns:
        list: 320 bits output
    """
    # n rounds
    for i in range(r):
        # a round contains 3 parts
        X = addConst(X, i)
        X = Sbox(X)
        X = Matrix(X)
    return X
    
def Invround(X,r):
    """inverse of the round function

    Args:
        X (list): 320 bits input

    Returns:
        list: 320 bits output
    """
    # 2 rounds
    for i in range(r):
        # a round contains 3 parts
        X = InvMatrix(X)
        X = InvSbox(X)
        X = addConst(X, i) 
    return X

def print_state(X: list, state_x=64, state_y=5) -> None:
    """print a state in column form

    Args:
        X (list): input state
    """
    # print 5*64 columns
    for y in range(state_y):
        #print("\n")
        lane_print = ""
        for x in range(state_x):
            # now start convert binary column to int
            # get the binary column
            lane_print += str(X[index_xy(x,y)]) if X[index_xy(x,y)] else "0"
        print(lane_print)
    print("------")
    for y in range(state_y):
        #print("\n")
        lane_print_0x = "0x"
        for x in range(0, state_x, 4):
            # now start convert binary column to int
            # get the binary column
            tmp = ""
            for i in range(4):
                tmp += str(X[index_xy(x+i,y)]) if X[index_xy(x+i,y)] else "0"
            lane_print_0x += hex(int(tmp, 2)).upper()[2:]
        print(lane_print_0x)
    print("------")

def index_xy(x: int, y: int) -> int:
    """return the index of coordinates x, y

    Args:
        x (int): x coordinate
        y (int): y coordinate

    Returns:
        int: index of x, y
    """
    x, y = x%64, y%5
    return 64 * y + x

def hex2bin(Hex_in, Bin_len=64):
    Bin_out = []
    for j in range(Bin_len):
        Bin_out.append(Hex_in >> ( Bin_len -1 - j ) & 0x1)
    return Bin_out

def index_z(z: int)-> int:
    """return the index of coordinates z

    Args:
        z (int): z coordinate

    Returns:
        int: index of z
    """
    z = (z + 64)%64
    return z

def bin2int(a:list) -> int:
    """把[1,0,1,0..,0]这类二进制list转成int
    """
    b = ""
    for i in a:
        b += str(i)
    return int(b, 2)

def location2binvalue(location:list):
    bin_v = [0 for i in range(64) ]
    for i in range(64):
        if i in location:
            bin_v[i] = 1
    print(bin_v)
    return bin_v

def binvalue2location(bin_v:list):
    loc_v = []
    for i in range(64):
        if bin_v[i] == 1:
            loc_v.append(i)
    print(loc_v)
    return loc_v


def print_x(X: list, state_x=64) -> None:
    """print a state in column form

    Args:
        X (list): input row
    """
    # print a row
    lane_print = ""
    for x in range(state_x):
        lane_print += str(X[x]) if X[x] else "0"
    # print(lane_print)
    # print("------")
    lane_print_0x = "0x"
    for x in range(0, state_x, 4):
        tmp = ""
        for i in range(4):
            tmp += str(X[x+i]) if X[x+i] else "0"
        lane_print_0x += hex(int(tmp, 2)).upper()[2:]
    # print(lane_print_0x)
    # print("------")
    return lane_print_0x

def hex_list_to_bit_list(hex_list):
    bit_list = []
    for hex_num in hex_list:
        # 将每个16进制数转换为64位的二进制字符串，并去掉前缀'0b'
        hex_num = int(hex_num,16)
        bit_str = bin(hex_num)[2:].zfill(64)
        # 将二进制字符串转换为列表，并添加到最终的位列表中
        bit_list.extend([int(bit) for bit in bit_str])
    return bit_list

def convert_diff_to_bit_list(Diff):
    bit_lists = []
    for hex_list in Diff:
        bit_list = hex_list_to_bit_list(hex_list)
        bit_lists.append(bit_list)
    return bit_lists

if __name__ == '__main__':
    R = declare_ring([Block('X', 320),'u'], globals() )
    Diff = [R(0) for r in range(9)]
    ############# 4rSFS ############## 
    Diff[0]   = [0x9000000000040000,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000]
    Diff[1]    = [0x9000000000040000,
                0x9000000000040000,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000]
    Diff[2]    = [0x1040120900040000,
                0x1000080001040004,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000]
    Diff[3]   = [
                0x10000A0800040004,
                0x0040120901040004,
                0x1000080001040004,
                0x10401A0101040004,
                0x1040100100000000
                ]
    
    Diff[4]    = [0x904088490145a084,
                0x10428a4101248000,
                0x08400c2001821006,
                0x114602278c44c186,
                0x10e0902102082008]
    
    Diff[5]   = [
                0x916488078DEC710E,
                0x88A41A6C83EBC10E,
                0x08C014620EEA3186,
                0x19020C6304EBF008,
                0x01C41A6F8F25E182
                ]
    Diff[6]    = [0xc1824ac20aa400cb,
                0x14831e8a81a4814e,
                0x14831e0281a48183,
                0xe30040611a1b4881,
                0x320000ab913b484c]
    
    Diff[7]   = [0xF7835EEB9BBFC9CF,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000,
                0x0000000000000000
                ]
    Diff[8] = [
                0x0000000000000000,
                0x0000001000000000,
                0x0000000000000000,
                0x0000000000000000,
                0x0000001000000000
    ]
    
    diff_bit_lists = convert_diff_to_bit_list(Diff)
    out_first = diff_bit_lists[8]
    
    for i in range(320):
        if out_first[i] ==1:
            out_first[i] = R(1)
        else:
            out_first[i] = R(0)
    out_first = Matrix(out_first)
    print(print_state(out_first))