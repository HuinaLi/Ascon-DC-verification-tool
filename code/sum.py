### compute the number of Active Sbox in one Ascon 320-State
###

from RoundF_anf import *

def compute_as_number(test:list):
    state = test
    res = []
    for s in state:
        res.append([int(x) for x in bin(int(s,16))[2:].rjust(64,'0')])
    # print(res[0])
    sum = 0
    out = []
    for i in range(64):
        n = 0
        for j in range(len(res)):
            n += res[j][i]
        out.append(n)
        if n >= 1:
            sum += 1
        else:
            continue
    # print(sum)

    for i in range(64):
        if out[i] != 0:
            out[i] = 1

    #### print the index of active sboxes in bin or hex form
    # print(out)
    bin_state = out + list(0 for _ in range(256))
    hex_state = []
    for y in range(5):
        value = bin2int(bin_state[64*y:64*(y+1)])
        hex_value = '0x' + format(value, 'x').zfill(16)  # Fill with zeros after '0x'
        hex_state.append(hex_value)
        
    # print(hex_state)
    return bin_state,hex_state




if __name__ == '__main__':
    R = declare_ring([Block('X', 320),'u'], globals() )
    test = [
        '0x180D824100A0B020',
        '0x9815C24B291489A2',
        '0x1800C20A28B489A0',
        '0x0488000080A03054',
        "0x84958043811008D6"
    ]
    
    out_first,diffstate = compute_as_number(test)
    ### print the output state of the next linear layer
    print(diffstate)
    for i in range(320):
        if out_first[i] ==1:
            out_first[i] = R(1)
        else:
            out_first[i] = R(0)
    out_first = Matrix(out_first)
    # print_state(out_first)
