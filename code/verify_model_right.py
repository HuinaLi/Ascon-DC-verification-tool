from RoundF_anf import *
from sage.sat.converters.polybori import CNFEncoder 
from sage.sat.solvers.dimacs import DIMACS
from pysat.card import *
from pysat.formula import IDPool
import argparse


#cnf_b0toa1:[B_x,y, B_x-r0,y, B_x-r1,y, A_x,y] 8 clauses
cnf_b0toa1 =  [
    [1, 2, 3, -4], 
    [1, 2, 4, -3], 
    [1, 3, 4, -2], 
    [2, 3, 4, -1], 
    [1, -2, -3, -4], 
    [2, -1, -3, -4], 
    [3, -1, -2, -4], 
    [4, -1, -2, -3]
]

# ascon_sbox 46 clauses  
cnf_chi = [
    [2 , 3 , 5 , 8], 
    [1 , 10 , 4 , -2],
    [1 , 5 , 7 , -6], 
    [1 , 8 , 9 , -5], 
    [10 , 2 , 5 , -4], 
    [2 , 3 , 9 , -1], 
    [2 , 4 , 5 , -10], 
    [4 , 5 , 6 , -2], 
    [4 , 8 , 9 , -7], 
    [1 , 2 , 4 , 7 , 8],
    [1 , 6 , -7 , -8], 
    [1 , 7 , -10 , -4], 
    [10 , 2 , -3 , -8], 
    [10 , 4 , -5 , -6], 
    [3 , 6 , -2 , -9],
    [5 , 8 , -1 , -7], 
    [5 , 8 , -2 , -3],
    [5 , 9 , -4 , -8],
    [6 , 7 , -1 , -5], 
    [6 , 9 , -4 , -5], 
    [7 , 9 , -1 , -5],
    [7 , 9 , -2 , -3], 
    [1 , 10 , 2 , 3 , -9],
    [10 , 2 , 4 , 6 , -9],
    [10 , 6 , 7 , 8 , -2],
    [1 , -5 , -8 , -9], 
    [10 , -1 , -2 , -4], 
    [2 , -1 , -3 , -9], 
    [3 , -2 , -6 , -8], 
    [4 , -1 , -10 , -2],
    [4 , -5 , -6 , -7],
    [5 , -2 , -4 , -6],
    [8 , -4 , -7 , -9],
    [1,  2,  9, -6,-7],
    [10 , 2 , 7 , -1 , -6], 
    [2 , 3 , 4 , -5 , -8], 
    [2 , 6 , 7 , -10 , -3],
    [10 , 4 , -3 , -7 , -8],
    [3 , 6 , -10 , -4 , -7], 
    [6 , 7 , -10 , -3 , -8], 
    [7 , 8 , -3 , -5 , -6], 
    [1 , -10 , -3 , -7 , -9],
    [3 , -1 , -4 , -6 , -9], 
    [9 , -10 , -3 , -4 , -5],
    [4 , 7 , 8 , -2 , -6 , -9], 
    [-1 , -10 , -5 , -7 , -9]
]
def generate_filename(Path, ROUNDS,Weight):
    # 初始化文件名的前缀部分
    filename = f"{Path}/{ROUNDS}round_w{Weight}"
    
    return filename

def check_dc_validity_newmodel(ROUNDS,Weight,start_rnd,Path,diff,state=320,rate=64):
    R = declare_ring( [Block( 'X', (3*ROUNDS)*state),'u' ], globals() )
    c_vars  = [[R(X(state*r + i)) for i in range(state)] for r in range(ROUNDS)]
    a_vars  = [[R(X(state*r + ROUNDS*state  + i)) for i in range(state)] for r in range(ROUNDS)]           
    b_vars  = [[R(X(state*r + 2*ROUNDS*state  + i)) for i in range(state)] for r in range(ROUNDS)]  
    ####### diff_pre ############  
    # c0--pc--a0--ps-->b0 --pl-->c1 --pc--a1--ps-->b1 --pl-->c2--pc--a2--ps-->b2--pl-->c3--pc--a3--ps-->b3
    ### Initialization ######
    Q = set()
    ###########Adding the Constraints of Difference and Value ##################
    # Q.add(c_vars[0][0] + 1)
    for r in range(ROUNDS):
        c_vars[r] = addConst(c_vars[r],r+start_rnd)
        for i in range(state):
            Q.add(c_vars[r][i] + a_vars[r][i])

    for r in range(ROUNDS):
        for i in range(state):
            a_vars[r][i] += diff[2*r][i] * R(u) 
        
        a_vars[r] = Sbox(a_vars[r])
        
        for i in range(state):
            if diff[2*r+1][i] == 1:
                d = a_vars[r][i] / R(u) 
                if d == 1:
                    pass
                elif d == 0:
                    print ( diff[2*r+1][i], d )
                    print( "Impossible" )
                    exit(0)
                else:
                    Q.add(a_vars[r][i]/R(u) + 1) 
            else:
                d = a_vars[r][i] / R(u) 
                if d == 0:
                    pass
                elif d == 1:
                    print ( diff[2*r+1][i], d )
                    print( "Impossible" )
                    exit(0)
                else:
                    Q.add(a_vars[r][i]/R(u)) 
        

    filename = generate_filename(Path, ROUNDS, Weight)
    filename += ".cnf"
    solver = DIMACS(filename = filename)
    e = CNFEncoder(solver, R)
    e(list(Q))
    solver.write()

    with open(filename, "r") as f:
        cnf_info = f.readline().split(" ")
        var_num, clause_num = int(cnf_info[2]), int(cnf_info[3])
        ls_cnf = f.read()
    # print(var_num,clause_num)

    constraint_cnf = " "
    # cnf_b0toa1: 8 clauses 
    row = [0]*4
    for r in range(ROUNDS-1): 
        for y in range(5):
            for x in range(rate):   
                # row [B0 B1 B2 A]
                if y == 0:
                    row = [(2*ROUNDS + r)*state + index_xy(x,y), (2*ROUNDS + r)*state +index_xy(x-19,y), (2*ROUNDS + r)*state +index_xy(x-28,y), (r+1)*state + index_xy(x,y)]
                if y == 1:
                    row = [(2*ROUNDS + r)*state +index_xy(x,y), (2*ROUNDS + r)*state +index_xy(x-61,y), (2*ROUNDS + r)*state +index_xy(x-39,y), (r+1)*state + index_xy(x,y)]
                if y == 2:
                    row = [(2*ROUNDS + r)*state +index_xy(x,y), (2*ROUNDS + r)*state +index_xy(x-1,y), (2*ROUNDS + r)*state +index_xy(x-6,y), (r+1)*state + index_xy(x,y)]
                if y == 3:
                    row = [(2*ROUNDS + r)*state +index_xy(x,y), (2*ROUNDS + r)*state +index_xy(x-10,y), (2*ROUNDS + r)*state +index_xy(x-17,y), (r+1)*state + index_xy(x,y)]
                if y == 4:
                    row = [(2*ROUNDS + r)*state +index_xy(x,y), (2*ROUNDS + r)*state +index_xy(x-7,y), (2*ROUNDS + r)*state +index_xy(x-41,y), (r+1)*state + index_xy(x,y)]
                    
                for i in range(len(cnf_b0toa1)):
                    CNF_clause= ""
                    for j in range(len(cnf_b0toa1[i])):
                        temp = int(cnf_b0toa1[i][j])
                        if temp > 0 :
                            CNF_clause += str(row[ temp-1] + 1) + " "
                        else:
                            CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                    CNF_clause += '0'
                    constraint_cnf += CNF_clause + "\n"
                    clause_num += 1 

    row = [0]*10
    for r in range(ROUNDS): 
        for x in range (rate):   
            row = [(ROUNDS + r)*state + index_xy(x,0), (ROUNDS + r)*state + index_xy(x,1), (ROUNDS + r)*state + index_xy(x,2), (ROUNDS + r)*state + index_xy(x,3), (ROUNDS + r)*state + index_xy(x,4),\
                   (2*ROUNDS + r)*state + index_xy(x,0), (2*ROUNDS + r)*state  + index_xy(x,1), (2*ROUNDS + r)*state + index_xy(x,2), (2*ROUNDS + r)*state  + index_xy(x,3), (2*ROUNDS + r)*state  + index_xy(x,4)]
            for i in range (len(cnf_chi)):
                CNF_clause= ""
                for j in range(len(cnf_chi[i])):
                    temp = int(cnf_chi[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                constraint_cnf += CNF_clause + "\n"
                clause_num += 1 

    with open(filename, "w") as f:
        f.write(f"p cnf {var_num} {clause_num}\n")
        f.write(ls_cnf)
        f.write(constraint_cnf)

    print(f"New DC Verify Model Constructed:) var_num:{var_num - 1}, clause_num:{clause_num}")


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="Adding initialization+Obj")
    parse.add_argument("-r", "--rounds", type=int, help="number of rounds")
    parse.add_argument("-f", "--path", type=str, help="cnf file path")
    parse.add_argument("-w", "--weight", type=int, help="weight")
    parse.add_argument("-m", "--stratrnd", type=int, help="start_rnd")
    args = parse.parse_args()


    check_dc_validity_newmodel(args.rounds, args.weight,args.stratrnd, args.path)
