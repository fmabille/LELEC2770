import numpy as np
import aes
import sys
import itertools
import os
from sbox import sbox
from random import randint
from Crypto.Cipher import AES
from tqdm import tqdm
from ff import GF2int, init_lut
import time
import glob, os
from threading import Thread
from Master import Master
from MiniCircuit import MiniCircuit
from Secret import Secret
from SubCircuit import SubCircuit

FIELD_EXPONENT = 8
init_lut(generator=3, prim=0x11b, c_exp=FIELD_EXPONENT)

def test_mult():
	key_cipher = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v1 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v2 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	sub = Master.get_one_sub(key_cipher)

	shares1 = Master.get_shares(v1,sub)
	shares2 = Master.get_shares(v2,sub)
	sub.initShares(shares1)
	for s,mini in enumerate(sub.minicircuits):
		mini.state2 = shares2[s]

	sub.multiply(inputs1=[mini.state2 for mini in sub.minicircuits])

	reconstruct = Master.reconstructShares(sub)
	if not np.array_equal(v1*v2,reconstruct):
		return 0
	else:
		return 1

def test_Sbox():
	key_cipher = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	sub = Master.get_one_sub(key_cipher)

	shares = Master.get_shares(v,sub)
	sub.initShares(shares)
	sub.SubBytes()
	reconstruct = Master.reconstructShares(sub)
	if not np.array_equal(np.array(sbox[np.array(v,dtype=int)],dtype=GF2int),reconstruct):
		return 0
	else:
		return 1

def test_squaring():
	key_cipher = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	sub = Master.get_one_sub(key_cipher)

	shares = Master.get_shares(v,sub)
	sub.initShares(shares)
	sub.square()
	reconstruct = Master.reconstructShares(sub)

	if not np.array_equal(v*v,reconstruct):
		return 0
	else:
		return 1

def test_addKey():
	key_cipher = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	sub = Master.get_one_sub(key_cipher)

	shares = Master.get_shares(v,sub)
	sub.initShares(shares)
	sub.addKey(0)
	reconstruct = Master.reconstructShares(sub)

	if not np.array_equal(v + key_cipher ,reconstruct):
		return 0
	else:
		return 1

def test_Sharing():

	key_cipher = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	v = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	sub = Master.get_one_sub(key_cipher)

	shares = Master.get_shares(v,sub)
	sub.initShares(shares)
	reconstruct = Master.reconstructShares(sub)

	if not np.array_equal(v,reconstruct):
		return 0
	else:
		return 1


def test_AES():
	# INIT KEYS AND PLAINTEXT

	key1 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	key2 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
	key3 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)

	key1 = "".join(format(y, '02x') for x in key1 for y in x)
	key2 = "".join(format(y, '02x') for x in key2 for y in x)
	key3 = "".join(format(y, '02x') for x in key3 for y in x)

	key_cipher = np.array([[GF2int(0) for i in range(4)] for j in range(4)], dtype=GF2int)
	plain_text = np.array([[GF2int(0) for i in range(4)] for j in range(4)], dtype=GF2int)

	plain_text_str = "".join(format(y, '02x') for x in plain_text for y in x)
	key_cipher_str = "".join(format(y, '02x') for x in key_cipher for y in x)

	aes_ref = AES.new(key_cipher_str)
	cipher_ref_str = aes_ref.encrypt(plain_text_str).encode("hex")
	W = aes.ExpandRoundKey(key_cipher)
	master = Master(key_cipher,4)
	keys = [key1,key2,key3]
	sub =  SubCircuit(np.array([MiniCircuit(keys[s%3],keys[(s+1)%3],W) for s in range(3)]))

	randomness = sub.getCorrRandom();
	shares = [Secret(),Secret(),Secret()]
	for s in range(0,3):
		shares[s].alpha = randomness[s]
		shares[s].x = plain_text + randomness[(s-1)%3]
	W = aes.ExpandRoundKey(key_cipher)
	sub.initShares(shares)
	sub.AES()

	shared = master.reconstructShares(sub)

	state = aes.AES(key_cipher,plain_text)
	if(not np.array_equal(state,shared)):
		return 0
	else:
		return 1


if test_Sharing():
	print("TEST SHARING PASSED")
else:
	print("<TEST SHARING FAILED>")

if test_addKey():
	print("TEST ADDKEY PASSED")
else:
	print("<TEST ADDKEY FAILED>")

if test_squaring():
	print("TEST SQUARING PASSED")
else:
	print("<TEST SQUARING FAILED>")

if test_mult():
	print("TEST MULT PASSED")
else:
	print("<TEST MULT FAILED>")

if test_Sbox():
	print("TEST SBOX PASSED")
else:
	print("<TEST SBOX FAILED>")

if test_AES():
	print("TEST AES PASSED")
else:
	print("<TEST AES FAILED>")
