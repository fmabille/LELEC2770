# -*- coding: utf-8 -*-
"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Secure 2-party computation

Oblivious Transfer
"""

''' Library needed for the Oblivious Transfer '''

# AES
from Crypto.Cipher import AES
# Python info
import sys
import gmpy
from Crypto.Random.random import randint


''' Class for key generation '''
class AES_key:
    def __init__(self, length = 128, value =  None, typeofvalue = None, nbr_zero = 108):
        # Length corresponds to the number of bits
        # for instance: 128 bits = 16 bytes (= 8 hex)
        self.rep_bin = None
        self.rep_bin_str = None
        self.rep_int = None
        self.rep_byt = None
        self.rep_byt_str = None
        self.rep_hex = None
        self.rep_AES_str = None
        if value == None:
            if nbr_zero != 0:
                self.rep_bin = [0]*nbr_zero #[random.randrange(1) for i in range(nbr_zero)]
                self.rep_bin += [randint(0,1) for i in range(length-nbr_zero)]
            else:
                self.rep_bin = [randint(0,1) for i in range(length-nbr_zero)]
            self.__BinToInt()
            self.__BinToByt(length)
            self.__BinToHex(length)
            self.__BytToBytStr()
            self.__BinToBinStr()
            self.rep_AES_str = self.rep_byt_str
        else:
            if typeofvalue == "bin":
                self.rep_bin = value
                self.__BinToInt()
                self.__BinToByt(length)
                self.__BinToHex(length)
                self.__BytToBytStr()
                self.__BinToBinStr()
                self.rep_AES_str = self.rep_byt_str
            if typeofvalue == "byt":
                self.rep_byt = value
                self.__BytToInt()
                self.__IntToBin(length)
                self.__BinToHex(length)
                self.__BytToBytStr()
                self.__BinToBinStr()
                self.rep_AES_str = self.rep_byt_str
            if typeofvalue == "int":
                self.rep_int = value
                self.__IntToBin(length)
                self.__BinToByt(length)
                self.__BinToHex(length)
                self.__BytToBytStr()
                self.__BinToBinStr()
                self.rep_AES_str = self.rep_byt_str
            if typeofvalue == "hex":
                self.rep_hex = value
                self.__HexToInt()
                self.__IntToBin(length)
                self.__BinToByt(length)
                self.__BytToBytStr()
                self.__BinToBinStr()
                self.rep_AES_str = self.rep_byt_str
            if typeofvalue == "bytstr":
                self.rep_byt_str = value
                self.rep_AES_str = value
                self.__BytStrToInt()
                self.__IntToBin(length)
                self.__BinToByt(length)
                self.__BinToHex(length)
                self.__BinToBinStr()
            if typeofvalue == "binstr":
                self.rep_bin_str = value
                self.__BinStrToInt()
                self.__IntToBin(length)
                self.__BinToByt(length)
                self.__BinToHex(length)
                self.__BytToBytStr()
                self.rep_AES_str = self.rep_byt_str
            if typeofvalue != "bin" and typeofvalue != "byt" and typeofvalue != "int" and typeofvalue != "hex" and typeofvalue != "bytstr" and typeofvalue != "binstr":
                print("The constructor didn't match the criterion.")
                return None



    def __IntToBin(self, length = None):
        self.rep_bin = []
        r = self.rep_int
        while r > 0:
            b = r % 2
            self.rep_bin.append(b)
            r = r // 2

        if length != None:
            if len(self.rep_bin) < length:
                fill = length-len(self.rep_bin)
                for i in range(fill):
                    self.rep_bin.append(0)
        self.rep_bin.reverse()

    def __IntToHex(self, length = None):
        self.rep_hex = []
        r = self.rep_int
        while r > 0:
            b = r % pow(2,16)
            self.rep_hex.append(b)
            r = r // pow(2,16)

        if length != None:
            if len(self.rep_hex) < length:
                fill = length-len(self.rep_hex)
                for i in range(fill):
                    self.rep_hex.append(0)
        self.rep_hex.reverse()

    def __IntToByt(self, length = None):
        self.rep_byt = []
        r = self.rep_int
        while r > 0:
            b = r % pow(2,8)
            self.rep_byt.append(b)
            r = r // pow(2,8)

        if length != None:
            if len(self.rep_byt) < length:
                fill = length-len(self.rep_byt)
                for i in range(fill):
                    self.rep_byt.append(0)
        self.rep_byt.reverse()

    def __BinToInt(self):
        self.rep_int = 0
        length = len(self.rep_bin)
        for i in range(length):
            self.rep_int += pow(2,i)*self.rep_bin[length-1 - i]

    def __BinToByt(self, length = None):
        self.__BinToInt()
        if length != None:
            self.__IntToByt(length//8)
        else:
            self.__IntToByt()

    def __BinToHex(self, length = None):
        self.__BinToInt()
        if length != None:
            self.__IntToHex(length//16)
        else:
            self.__IntToHex()

    def __BinToBinStr(self):
        self.rep_bin_str = ''
        length = len(self.rep_bin)
        for i in range(length):
            self.rep_bin_str += str(self.rep_bin[i])

    def __BinStrToInt(self):
        self.rep_int = int(self.rep_bin_str,2)

    def __BytToInt(self):
        self.rep_int = 0
        length = len(self.rep_byt)
        for i in range(length):
            self.rep_int += pow(pow(2,8),i)*self.rep_byt[length-1 - i]

    def __BytToBin(self, length = None):
        self.__BytToInt()
        if length != None:
            self.__IntToBin(length//8)
        else:
            self.__IntToBin()


    def __BytToHex(self, length = None):
        self.__BytToInt()
        if length != None:
            self.__IntToHex(length//16)
        else:
            self.__IntToHex()

    def __HexToInt(self):
        self.rep_int = 0
        length = len(self.rep_hex)
        for i in range(length):
            self.rep_int += pow(pow(2,8),i)*self.rep_hex[length-1 - i]

    def __HexToBin(self, length = None):
        self.__HexToInt()
        if length != None:
            self.__IntToBin(length)
        else:
            self.__IntToBin()

    def __HexToByt(self, length = None):
        self.__HexToInt()
        if length != None:
            self.__IntToByt(length//8)
        else:
            self.__IntToByt()

    def __BytToBytStr(self):
        length = len(self.rep_byt)
        self.rep_byt_str = ''
        if sys.version_info.major > 2:
            self.rep_byt_str = b''

        for i in range(length):
            self.rep_byt_str += bytes(bytearray([self.rep_byt[i]]))


    def __BytStrToInt(self):
        if sys.version_info.major > 2:
            self.rep_int = int.from_bytes(self.rep_byt_str,'big')
        else:
            self.rep_int = int(self.rep_byt_str.encode('hex'),16)


    def encrypt(self, m):
        AES_obj = AES.new(self.rep_AES_str)
        if m in [0,1]:
            m_prime = AES_key(value=m, typeofvalue= 'int')
            c = AES_obj.encrypt(m_prime.rep_AES_str)
        else :
            c = AES_obj.encrypt(m)
        return c

    def decrypt(self, c):
        AES_obj = AES.new(self.rep_AES_str)
        d = AES_obj.decrypt(c)
        return d


def El_Gamal_ParamGen():
    p = 4
    while not gmpy.is_prime(p):
        r = randint(0,2**64)
        q = gmpy.next_prime(2**64+r)
        p = 2*q+1

    g_prime = randint(1,int(p-1))
    g = pow(g_prime,2,p) # generator of the group
    assert pow(g,q,p) == 1
    G = g,p,q
    x = randint(1,int(q-1)) # secret key
    y = pow(g,x,p) # public key
    pk = El_Gamal_PublicKey(G,y)
    sk = El_Gamal_SecretKey(G,x)
    return pk,sk


class El_Gamal_PublicKey:
    def __init__(self,G,y):
        self.G = G
        self.y = y

    def random(self):
        q = self.G[2]
        return randint(1,int(q-1))

    def encrypt(self,m):
        assert len(bin(m))<=22 # message length must be less than 22 bits
        g = self.G[0]
        p = self.G[1]

        r = self.random()
        c1 = pow(g,r,p)
        c2 = (pow(g,m,p)*pow(self.y,r,p))%p

        return El_Gamal_Ciphertext(p,c1,c2)

class El_Gamal_SecretKey:

    def __init__(self,G,x):
        self.G = G
        self.x = x

    def decrypt(self,c):
        assert isinstance(c,El_Gamal_Ciphertext)
        g = self.G[0]
        p = self.G[1]

        def dLog(g,g_m):
            #TODO: optimize this
            a = 1
            i = 0
            while i<2**20:
                if a == g_m :
                    return i
                else :
                    a = a*g % p
                    i += 1
            return None # no DLog < 2**32 found

        c1 = c.c1
        c2 = c.c2
        c1_prime = pow(c1,self.x,p)
        g_m = gmpy.divm(c2,c1_prime,p)
        m = dLog(g,g_m)
        return m


class El_Gamal_Ciphertext:

    def __init__(self,p,c1,c2):
        self.p = p
        self.c1 = c1
        self.c2 = c2

    def __add__(self,other):
        return El_Gamal_Ciphertext(self.p,self.c1*other.c1,self.c2*other.c2)

    def __neg__(self):
        inv_c1 = gmpy.invert(self.c1,self.p)
        inv_c2 = gmpy.invert(self.c2,self.p)
        return El_Gamal_Ciphertext(self.p,inv_c1,inv_c2)

    def __sub__(self, other):
        return self.__add__(other.__neg__())

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, alpha):
        return El_Gamal_Ciphertext(self.p,pow(self.c1,alpha,self.p),pow(self.c2,alpha,self.p))

    def __rmul__(self, other):
        return self.__mul__(other)
