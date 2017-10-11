# -*- coding: utf-8 -*-
"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Secure 2-party computation

Oblivious Transfer
"""

''' Libraries needed for the Oblivious Transfer '''
from utils import El_Gamal_ParamGen,El_Gamal_PublicKey,El_Gamal_SecretKey,El_Gamal_Ciphertext
from utils import AES_key
from Crypto.Random import random

class Sender:#P1
    def __init__(self, msg_0, msg_1):
        assert isinstance(msg_0,AES_key)
        assert isinstance(msg_1,AES_key)
        self.m_0 = msg_0 # must be aes key
        self.m_1 = msg_1 # must be aes key

    def response(self,c,pk):
        c_0 = ((pk.encrypt(1)-c)*self.m_0.rep_int) + (pk.random()*c)
        c_1 = ((pk.encrypt(1)-c)*pk.random()) + (c*self.m_1.rep_int)
        return c_0, c_1

class Receiver: #P2
    def __init__(self):
        self.pk,self.sk = El_Gamal_ParamGen()

    def challenge(self,b):
        return self.pk.encrypt(b)

    def decrypt_response(self,c_0,c_1,b):
        if b == 0:
            s_r = self.sk.decrypt(c_0)
        else:
            s_r = self.sk.decrypt(c_1)
        return AES_key(value = s_r, typeofvalue='int')


def test_OT():
    b = random.getrandbits(1)
    Bob = Receiver()

    k0 = AES_key()
    k1 = AES_key()
    Alice = Sender(k0,k1)

    c = Bob.challenge(b)
    pk = Bob.pk

    c0,c1 = Alice.response(c, pk)
    k = Bob.decrypt_response(c0,c1,b)

    print(k0.rep_int,k1.rep_int,b,k.rep_int)
