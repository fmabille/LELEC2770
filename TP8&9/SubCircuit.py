import numpy as np
import aes
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
from MiniCircuit import MiniCircuit,twoOutOfthree

class SubCircuit(Thread):
	minicircuits = []

	def __init__(self,keys,key_cipher=None):
		Thread.__init__(self)

		if key_cipher is not None:
			self.minicircuits = [MiniCircuit(keys[0],keys[1]),MiniCircuit(keys[1],keys[2]),MiniCircuit(keys[2],keys[0])]
			W = aes.ExpandRoundKey(key_cipher)
			for mini in self.minicircuits:
				mini.W = W
		else:
			self.minicircuits = keys

	def getCorrRandom(self):
		""" return the correlated randmness from all the minicirucits"""
		randomness = []
		for i in xrange(3):
			randomness.append(self.minicircuits[i].corrRandom())
		return randomness

	def initShares(self,shares):
		""" set the initial shares to the mini circuits"""
		for i,mini in enumerate(self.minicircuits):
			mini.state = shares[i]

	def addKey(self,r=0):
		""" ask all the minicircuits to perform key additon """
		for mini in self.minicircuits:
			mini.addKey(r)

	def square(self):
		""" ask all the minicircuits to perform a suaqring of its state"""
		for mini in self.minicircuits:
			mini.state = mini.square(mini.state)

	def ShiftRows(self):
		for mini in self.minicircuits:
			mini.ShiftRows()

	def multiply(self,inputs1=None,inputs2=None,outputs=None):
		randomness = self.getCorrRandom()
		if inputs1 is None:
			inputs1 = [mini.state for mini in self.minicircuits]

		if inputs2 is None:
			inputs2 = [mini.state for mini in self.minicircuits]

		tab = []
		for s,(mini, rand) in enumerate(zip(self.minicircuits, randomness)):
			tab.append(mini.getC(inputs1[s], inputs2[s], rand))

		if outputs is None:
			outputs = [mini.state for mini in self.minicircuits]

		for s,out in enumerate(outputs):
			secret = twoOutOfthree(tab[s], tab[(s-1)%3])
			outputs[s].x = secret.x
			outputs[s].alpha = secret.alpha

	def MixColumns(self):
		for mini in self.minicircuits:
			mini.MixColumns()

	def preloadShares(self,preloadedShares):
		""" multiples shares for different plain texts """
		self.preloadedShares = preloadedShares

	def SubBytes(self):
		#y2
		for mini in self.minicircuits:
			mini.y2 = mini.square(mini.state)

		#y3
		self.multiply(inputs1=[mini.y2 for mini in self.minicircuits],inputs2=[mini.state for mini in self.minicircuits],outputs=[mini.y3 for mini in self.minicircuits])
		#y12
		# ...
		#y15
		# ...
		#y240
		# ...
		#y252
		# ...
		#y254
		# ...
		#affine transform
		for mini in self.minicircuits:
			mini.affine()

	def write_output(self,filename,master):
		output = master.reconstructShares(self)
		with open(filename,"a") as file:
			for x in output.reshape(16):
				file.write("{:02X}".format(x)+"\n")

	def run(self,master,id,bar=0):
		filename = "subcircuit"+str(id)+".hex"
		if bar:
			l = tqdm(self.preloadedShares)
		else:
			l = self.preloadedShares

		for shares in l:
			self.initShares(shares)
			self.AES()
			self.write_output(filename,master)

	def AES(self):
	    self.addKey(0)
	    for r in range(1,10):
	        self.SubBytes()
	        self.ShiftRows()
	        self.MixColumns()
	        self.addKey(r)
	    self.SubBytes()
	    self.ShiftRows()
	    self.addKey(10)
