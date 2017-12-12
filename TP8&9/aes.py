
import numpy as np
from sbox import sbox
from ff import GF2int


def GF_from_bits(b):
    t = 0
    for i, val in enumerate(b):
        t += val * (2**i)
    return GF2int(t)


# converts to bits with MSB at last position
def bits(gf):
    b = bin(gf)[2:]
    # pad
    bp = "0" * (8 - len(b)) + b
    bp = bp[::-1]
    return np.array([int(digit) for digit in bp])


def affine(b,add=1):
    mat = np.array([
        [1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1]])
    p = np.array([1, 1, 0, 0, 0, 1, 1, 0]).T

    bb = bits(b)
    if add:
        af = np.mod(np.dot(mat, bb) + p, 2)
    else:
        af = np.mod(np.dot(mat,bb),2)
    return GF_from_bits(af)

def affine2(b):
    mat = np.array([
        [1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1]])
    p = np.array([1, 1, 0, 0, 0, 1, 1, 0]).T

    bb = bits(b)
    af = np.mod(np.dot(mat, bb) , 2)
    return GF_from_bits(af)

def inverse_or_zero(i):
    if i == GF2int(0):
        return i
    else:
        return i.inverse()


def SubBytes(state):
    inverse_or_zero_v = np.vectorize(inverse_or_zero,otypes=[GF2int])
    inv_state = inverse_or_zero_v(state)

    affinev = np.vectorize(affine, otypes=[GF2int])
    affine_state = affinev(inv_state)

    return affine_state


def ShiftRows(state):
    shifted = state.copy()
    shifted[0,:] = state[0,:]
    shifted[1,:] = state[1,[1,2,3,0]]
    shifted[2,:] = state[2,[2,3,0,1]]
    shifted[3,:] = state[3,[3,0,1,2]]
    return shifted


def mix_one_col(col):
    m = np.array([[GF2int(2), GF2int(3), GF2int(1), GF2int(1)],
                  [GF2int(1), GF2int(2), GF2int(3), GF2int(1)],
                  [GF2int(1), GF2int(1), GF2int(2), GF2int(3)],
                  [GF2int(3), GF2int(1), GF2int(1), GF2int(2)]], 
                 dtype=GF2int)
    return np.dot(m, col)


def MixColumns(state):
    # Apply the matrix multiplication (in GF) column by column
    mixed_state = np.empty_like(state)
    for i in range(4):
        mixed_state[:,i] = mix_one_col(state[:,i])

    return mixed_state


def AddRoundKey(key, state):
    return key + state

def SubBytes_4(state):
    inverse_or_zero_v = np.vectorize(inverse_or_zero , otypes=[GF2int])
    inv_state = inverse_or_zero_v(state)
    return inv_state

def Rcon(i):
    b = GF2int(1)
    for g in range(1,i):
        b = b * GF2int(2)

    return b


def ExpandRoundKey(key):
    Nk = 4;
    Nb = 16;
    Nr = 10;
    W = np.zeros([4 , (Nr+1)*4],dtype = GF2int)
    
    W.fill( GF2int(1))
    W[:4 , 0:4] = key
   
    for i in range(4, (Nr+1)*4):
        temp = np.array(W[:,i-1]);

        if i%Nk == 0:
            temp_v = temp[0]
            temp[0:3] = temp[1:4]
            temp[3] = temp_v
            temp = SubBytes(temp)
            temp[0] = temp[0] + Rcon(GF2int(i/Nk))
        W[:,i] = np.array(W[:,i-Nk] + temp)

    return W

def AES(key, pt):
    W = ExpandRoundKey(key)

    round_key = W[:, 4:8]
    state = AddRoundKey(W[: ,0:4], pt)

    for r in range(1,10):
                
        round_key = W[:,r*4:(r+1)*4]
        #round_key = key

        # SubBytes
        state = SubBytes(state)

        # ShiftRows
        state = ShiftRows(state)

        # Mixcolumns
        state = MixColumns(state)

        # AddRoundKey
        state = AddRoundKey(round_key, state)

    # last round:
    
    round_key = W[: , (10)*4:]

    # SubBytes
    state = SubBytes(state)

    # ShiftRows
    state = ShiftRows(state)

    # AddRoundKey
    state = AddRoundKey(round_key, state)

    return state
