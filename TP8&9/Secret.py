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
class Secret:
	def __init__(self,alpha,x):
		self.alpha = alpha
		self.x = x

	def __init__(self):
		self.alpha =  np.array([[GF2int(0) for i in range(4)] for j in range(4)], dtype=GF2int)
		self.x =  np.array([[GF2int(0) for i in range(4)] for j in range(4)], dtype=GF2int)