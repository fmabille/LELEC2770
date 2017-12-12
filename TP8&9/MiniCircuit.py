import numpy as np
import aes
import copy
import sys
import os
from random import randint
from Crypto.Cipher import AES
from tqdm import tqdm
from ff import GF2int, init_lut
import time
import glob, os
from threading import Thread
from Secret import Secret

class IVCounter(object):
    def __init__(self, start=0):
        self.value = long(start)
    def __call__(self):
        self.value += 1
        return '{0:016x}'.format(self.value)

class MiniCircuit(object):
	def __init__(self,key1,key2,W=None):
		self.key1 = key1
		self.key2 = key2
		self.ctr = IVCounter()
		self.W = W
		self.y3 = Secret()

	def setKeys(self,key1,key2,W):
		self.key1 = key1
		self.key2 = key2
		self.W = W
		self.ctr = IVCounter()

	def corrRandom(self):
		"""Return random correlated value array"""
		cnt = self.ctr.__call__()
		cipher1 = AES.new(self.key1)
		cipher2 = AES.new(self.key2)
		ct1 = cipher1.encrypt(cnt).encode("hex")
		ct2 = cipher2.encrypt(cnt).encode("hex")
		randomness = np.zeros([4,4],dtype=GF2int)
		for i in range(0,4):
			for j in range(0,4):
				randomness[i,j] = GF2int(int(ct2[(i*4+j)*2:(i*4+j)*2+2],16)) + GF2int(int(ct1[(i*4+j)*2:(i*4+j)*2+2],16))

		return randomness

	def addKey(self,Nr):
		""" Perfom the addition between W[:,(Nr)*4:(Nr+1)*4] and self.state """
		self.state.x = self.state.x + self.W[:,(Nr)*4:(Nr+1)*4]

	def affine(self):
		"""Affine transformation for Sbox"""
		for i in range(0,4):
			for j in range(0,4):
				self.state.x[i,j] = aes.affine(self.state.x[i,j],1)
				self.state.alpha[i,j] = aes.affine(self.state.alpha[i,j],0)

	def ShiftRows(self):
		self.state.x = aes.ShiftRows(self.state.x)
		self.state.alpha = aes.ShiftRows(self.state.alpha)

	def MixColumns(self):
		self.state.x = aes.MixColumns(self.state.x)
		self.state.alpha = aes.MixColumns(self.state.alpha)

	def getC(self,secret1,secret2,randomness):
		""" return the C value of this mini circuit. Used for multiplication """
                return (secret1.alpha * secret2.alpha) + (secret1.x * secret2.x) + randomness


	def square(self,a):
		""" return the secret out representing a^2 """
                out = Secret()
		out.alpha = a.alpha**2
                out.x = a.x**2
                return out


def twoOutOfthree(c1,c2):
	""" return secret from two part of three-out-of-three secret """
	s = Secret()
        s.alpha = c1 + c2
        s.x = c1
	return s
