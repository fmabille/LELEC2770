import numpy as np
import aes
from collections import Counter
import sys
import os
import random
import itertools
from random import randint
from Crypto.Cipher import AES
from tqdm import tqdm
from ff import GF2int, init_lut
import time
import glob, os
from threading import Thread
from SubCircuit import SubCircuit
from Secret import Secret

class Master:
	def __init__(self,key_cipher, subcircuits=[], lamb=1,createSub=False,flags=[]):
		self.key_cipher = key_cipher
		self.subcircuits = subcircuits
		self.flags = np.array(flags)

		if createSub:
			for i in range(0,lamb):
				key1 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
				key2 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
				key3 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)

				key1 = "".join(format(y, '02x') for x in key1 for y in x)
				key2 = "".join(format(y, '02x') for x in key2 for y in x)
				key3 = "".join(format(y, '02x') for x in key3 for y in x)
				self.subcircuits.append(SubCircuit([key1,key2,key3],key_cipher))

	def AES(self,plain_texts):
		self.plain_texts = plain_texts
		id = 0
		child_lst = []
		_lambda= len(self.subcircuits)

		for sub in self.subcircuits:
			newpid = os.fork()
			if newpid == 0: #child compute its shares
				random.seed(time.time())
				shares_pt = [] #Generate shares
				for plain_text in plain_texts:
					randomness = sub.getCorrRandom();
					shares = [Secret(),Secret(),Secret()]
					for s in range(0,3):
						shares[s].alpha = randomness[s]
						shares[s].x = plain_text + randomness[(s-1)%3]
					shares_pt.append(shares)

				sub.preloadShares(shares_pt)
				sub.run(self,id,id==0)
				os._exit(0)
			else:
				child_lst.append(newpid)
			id = id+1

		#parent child computes expected cipher
		expected_output = np.zeros(len(plain_texts)*16,dtype=int)
		for i,plain_text in enumerate(plain_texts):
			expected = aes.AES(self.key_cipher,plain_text)
			with open("expected.hex","a") as file:
				for j,x in enumerate(expected.reshape(16)):
					file.write("{:02X}".format(x)+"\n")
					expected_output[i*16 + j] = x

		for child in child_lst:
			pid, status = os.waitpid(child, 0)
			print("wait returned, pid = %d, status = %d" % (pid, status))

		## LOAD ALL FILES
		sub_index = np.array(range(_lambda),dtype=int)
		sub_outputs = np.zeros([_lambda,len(plain_texts)*16],dtype=int)
		stats = np.zeros([_lambda,2])

		for i in sub_index:
			with open("subcircuit%d.hex"%(i),'rb') as file:
				for j in range(len(plain_texts)*16):
					r = file.readline()
					sub_outputs[i,j] = int(r,16)

		for n_sub in range(_lambda):
			base = 0;

			while base < _lambda - (n_sub):
				sub_select = range(base,base+n_sub+1)
				if len(sub_select) != n_sub+1:
					continue

				result = 0

				rnd = randint(0,1)

				#Check the output of the master after majority vote
				for pl in range(len(plain_texts)*16):
					c = Counter(sub_outputs[sub_select,pl]).most_common()
					out_maj = c[0][0]
					unclear_maj = c[0][1] < ((n_sub+1)/2 +1)
					outputs_all = sub_outputs[sub_select,pl]

					if unclear_maj:
						arg = np.min([np.nonzero(outputs_all==c[0][0]),np.nonzero(outputs_all==c[1][0])])
						out_maj = outputs_all[arg]

					if(out_maj != expected_output[pl]):
						result = 1
						break

				for f in self.flags[sub_select]:
					if f!=0:
						result = 0

				stats[n_sub,0] = stats[n_sub,0] + 1
				stats[n_sub,1] = stats[n_sub,1] + result
				base = base + n_sub+1
		return stats

	@staticmethod
	def reconstructShares(sub):
		""" retreive the shared value in mini.state for self.minicircuits """
		return sub.minicircuits[0].state.alpha + sub.minicircuits[1].state.x

	@staticmethod
	def get_shares(v,sub):
		""" return the shares of v for subcircuit sub """
		#shares = [Secret(),Secret(),Secret()]
		shares = []
		random = sub.getCorrRandom()
		for i in range(0, len(random)):
			s = Secret()
			s.alpha = random[i]
			s.x = v + random[i-1%3]
			shares.append(s)
		return shares

	@staticmethod
	def get_one_sub(key_cipher):
		key1 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
		key2 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)
		key3 = np.array([[GF2int(randint(0,255)) for i in range(4)] for j in range(4)], dtype=GF2int)

		key1 = "".join(format(y, '02x') for x in key1 for y in x)
		key2 = "".join(format(y, '02x') for x in key2 for y in x)
		key3 = "".join(format(y, '02x') for x in key3 for y in x)

		return SubCircuit([key1,key2,key3],key_cipher)
