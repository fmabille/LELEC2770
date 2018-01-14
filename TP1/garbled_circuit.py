# -*- coding: utf-8 -*-
"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Secure 2-party computation

Garbled Circuit
"""

from utils import AES_key
from Crypto.Random import random
import OT

class gate:
    def __init__(self,gate_id,gate_0,gate_1,op,output_value=None,is_circuit_input=False,is_circuit_output=False):
        self.gate_id = gate_id
        self.gate_0 = gate_0
        self.gate_1 = gate_1
        self.op = op # 'AND', 'NAND', 'OR', 'NOR', 'XOR'
        self.output_value = output_value
        self.is_circuit_input = is_circuit_input
        self.is_circuit_output = is_circuit_output

    def evaluate(self):
        assert not (self.is_circuit_input and self.output_value==None) # input circuit gate must have an output value != None
        if self.gate_0.output_value == None :
            self.gate_0.evaluate()
            assert self.gate_0.output_value == 0 or self.gate_0.output_value == 1 # gate_0 must output a binary value
        if self.gate_1.output_value == None :
            self.gate_1.evaluate()
            assert self.gate_1.output_value == 0 or self.gate_1.output_value == 1 # gate_1 must output a binary value

        self.output_value = self.loc_eval(self.gate_0.output_value, self.gate_1.output_value)


    def loc_eval(self,x,y):
        if self.op == 'AND':
            return x and y
        elif self.op == 'NAND':
            return not (x and y)
        elif self.op == 'OR':
            return x or y
        elif self.op == 'NOR':
            return not (x or y)
        elif self.op == 'XOR':
            return x ^ y


class circuit:
    def __init__(self,G):
        '''
        G is the dictionary of the gates of the circuit {gate_id:gate_object}
        '''
        self.G = G

    def evaluate(self,inputs_dic):
        '''
        inputs_dic is a dictionary {gate_id:input_value}
        '''
        for gate in self.G.values():
            # erase previous evaluation
            gate.output_value = None
        for gate_id in inputs_dic :
            # load inputs
            self.G[gate_id].output_value = inputs_dic[gate_id]
        for gate in self.G.values():
            # evaluate output gates
            if gate.is_circuit_output :
                gate.evaluate()

# TEST CIRCUIT
gate_0 = gate('gate_0',None,None,'',is_circuit_input=True) # an input gate
gate_1 = gate('gate_1',None,None,'',is_circuit_input=True) # another input gate
gate_2 = gate('gate_2',None,None,'',is_circuit_input=True) # a third input gate
gate_3 = gate('gate_3',gate_0,gate_1,'AND') # gate_3 is gate_0 and gate_1
gate_4 = gate('gate_4',gate_2,gate_3,'XOR',is_circuit_output=True) # the output gate of the circuit (g_0 and g_1) xor g2

circ = circuit({'gate_0':gate_0,'gate_1':gate_1,'gate_2':gate_2,'gate_3':gate_3,'gate_4':gate_4})

circ.evaluate({'gate_0':1,'gate_1':1,'gate_2':0})
#print 'output of the circuit is',gate_4.output_value

# PAPER - ROCK - SCISSORS Circuit
gate_A = gate('igate_A',None,None,'',is_circuit_input=True) # input gate owned by P1
gate_B = gate('igate_B',None,None,'',is_circuit_input=True) # input gate owned by P1
gate_C = gate('igate_C',None,None,'',is_circuit_input=True) # input gate owned by P2
gate_D = gate('igate_D',None,None,'',is_circuit_input=True) # input gate owned by P2

gate_AB = gate('gate_AB',gate_A,gate_B,'AND') # g_A and g_B
gate_AC = gate('gate_AC',gate_A,gate_C,'AND') # g_A and g_C
gate_BC = gate('gate_BC',gate_B,gate_C,'AND') # g_B and g_C
gate_BxC = gate('gate_BxC',gate_B,gate_C,'XOR') # g_B xor g_C
gate_BD = gate('gate_BD',gate_B,gate_D,'AND') # g_B and g_D
gate_CD = gate('gate_CD',gate_C,gate_D,'AND') # g_C and g_D
gate_AD = gate('gate_AD',gate_A,gate_D,'AND') # g_A and g_D
gate_AxD = gate('gate_AxD',gate_A,gate_D,'XOR') # g_A xor g_D

gate_ACxBD = gate('gate_ACxBD',gate_AC,gate_BD,'XOR') # g_AC xor g_BD
gate_BCxCD = gate('gate_BCxCD',gate_BC,gate_CD,'XOR') # g_BC xor g_CD
gate_ABxAD = gate('gate_ABxAD',gate_AB,gate_AD,'XOR') # g_AB xor g_AD

gate_ACxBDxBCxCD = gate('gate_ACxBDxBCxCD',gate_ACxBD,gate_BCxCD,'XOR') # g_AC xor g_BD xor g_BC xor g_CD
gate_ACxBDxABxAD = gate('gate_ACxBDxABxAD',gate_ACxBD,gate_ABxAD,'XOR') # g_AC xor g_BD xor g_AB xor g_AD

gate_E = gate('gate_E',gate_ACxBDxABxAD,gate_BxC,'XOR',is_circuit_output=True) # g_AC xor g_BD xor g_AB xor g_AD xor g_B xor g_C
gate_F = gate('gate_F',gate_ACxBDxBCxCD,gate_AxD,'XOR',is_circuit_output=True) # g_AC xor g_BD xor g_BC xor g_CD xor g_A xor g_D

G = {'igate_A':gate_A,
     'igate_B':gate_B,
     'igate_C':gate_C,
     'igate_D':gate_D,
     'gate_AB':gate_AB,
     'gate_AC':gate_AC,
     'gate_BC':gate_BC,
     'gate_BxC':gate_BxC,
     'gate_BD':gate_BD,
     'gate_CD':gate_CD,
     'gate_AD':gate_AD,
     'gate_AxD':gate_AxD,
     'gate_ACxBD':gate_ACxBD,
     'gate_BCxCD':gate_BCxCD,
     'gate_ABxAD':gate_ABxAD,
     'gate_ACxBDxBCxCD':gate_ACxBDxBCxCD,
     'gate_ACxBDxABxAD':gate_ACxBDxABxAD,
     'gate_E':gate_E,
     'gate_F':gate_F}

PRS_circuit = circuit(G)

class garbler:

    def __init__(self,circuit,myinputs):
        self.circuit = circuit
        self.myinputs = myinputs # a dictionary {gate_id:value}
        for gate_id in self.myinputs:
            # verify myinputs are inputs of the circuit
            assert gate_id in self.circuit.G
            assert self.circuit.G[gate_id].is_circuit_input
            self.myinputs[gate_id] = random.getrandbits(1)
        self.output_table = {}
        self.garbled_table = {}

    def garble(self):

        self.output_table = {}
        self.garbled_table = {} # emptying tables

        for gate in self.circuit.G.values() :
            if not gate.is_circuit_output :
                k_0 = AES_key() # generate a random aes key
                k_1 = AES_key() # same
                self.output_table[gate.gate_id] = k_0,k_1


        for gate in self.circuit.G.values() :
            if not gate.is_circuit_input :
                gate_0 = gate.gate_0
                gate_1 = gate.gate_1
                K_0 = self.output_table[gate_0.gate_id] # K_0 = k_00, k_01
                K_1 = self.output_table[gate_1.gate_id] # K_1 = k_10, k_11
                c_list = []
                for i in range(2):
                    for j in range(2):
                        alpha = gate.loc_eval(i,j) # 'real' evaluation of the gate on i,j
                        if  gate.is_circuit_output :
                            m = alpha # 0 or 1
                        else :
                            K = self.output_table[gate.gate_id]
                            m = K[alpha].rep_AES_str # k_0 or k_1 (see above)

                        c = K_1[j].encrypt(m)
                        c_ij = K_0[i].encrypt(c)
                        c_list.append(c_ij)

                random.shuffle(c_list)
                self.garbled_table[gate.gate_id] = c_list
        return self.garbled_table

    def input_keys(self):
        my_input_keys = {}
        for gate_id in self.myinputs :
            K = self.output_table[gate_id]
            key = K[self.myinputs[gate_id]] # key = K[i] where i in [0,1] is my input
            my_input_keys[gate_id] = key
        return my_input_keys

    def oblivious_transfer(self,gate_id,c,pk):
        assert gate_id not in self.myinputs and self.circuit.G[gate_id].is_circuit_input # engage OT only on evaluator's inputs
        k0,k1 = self.output_table[gate_id]
        OT_Sender = OT.Sender(k0,k1)
        response = OT_Sender.response(c,pk)
        return response


class evaluator:

    def __init__(self,circuit,myinputs,OT_receiver):
        self.circuit = circuit
        self.myinputs = myinputs # a dictionary {gate_id:value}
        for gate_id in self.myinputs:
            # verify myinputs are inputs of the circuit
            assert gate_id in self.circuit.G
            assert self.circuit.G[gate_id].is_circuit_input
            assert self.myinputs[gate_id] in [0,1]
        self.OT_receiver = OT_receiver

    def evaluate(self, garbled_table, my_input_keys, other_input_keys): #my_input_keys = BOB input keys / #other = ALice inputkey
        def check_decryption(d):
             '''
             This function checks if the decryption is a 'valid' one i.e.
             either a plaintext of 0 or 1
             either an AES_key of 20 bits padded with 98 zeros.
             '''
             key = AES_key(value=d, typeofvalue = 'bytstr')
             if  key.rep_int in [0,1]:
                 return key.rep_int
             elif not '1' in key.rep_bin_str[:98]:
                 return key.rep_byt_str
             else :
                 return None

        def evaluate_garbled_gate(gate):
            if gate.gate_0.output_value == None:
                evaluate_garbled_gate(gate.gate_0)
            if gate.gate_1.output_value == None:
                evaluate_garbled_gate(gate.gate_1)

            for i in garbled_table[gate.gate_id]:
                """ @student
                i is an element of the garbled table which means that it is
                a double encryption of the output of the gate (either an AES key or a bit)
                so you have to decrypt it (twice) first to obtain d and then you can call check_decryption(d)
                To decrypt i, you have to use the keys that are the outputs of the gate_0, and gate_1.
                Only one of the four decryption will pass the check_decryption method, the three others will
                return None. You must store the result in the output_value of the gate.
                """
                d = gate.gate_0.output_value.decrypt(i)
                e = gate.gate_1.output_value.decrypt(d)
                if check_decryption(e) is not None:
                    if gate.is_circuit_output:
                        gate.output_value = check_decryption(e)
                    else:
                        gate.output_value = AES_key(value=e,typeofvalue='bytstr')

            #gate.output_value = AES_key(value=d,typeofvalue='bytstr')
            """ @student
            evaluate_garbled_gate() has no return value (and it is not suppose to)
            either the gate is an output gate and then the output is the decryption of one of the garbled_table element
            either the gate is an internal gate and then the output is an AES_key thus
            gate.output_value = AES_key(value=d,typeofvalue='bytstr') where d is the (second) decryption
            """
            ##### Complete here #####
            #
            # evaluate a garbled_gate and store the result in gate.output_value
            #
            #####
        circuit_outputs = {}
        for gate_id in my_input_keys :
            # load inputs BOB
            self.circuit.G[gate_id].output_value = my_input_keys[gate_id]
        for gate_id in other_input_keys:
            # load inputs Alice
            self.circuit.G[gate_id].output_value = other_input_keys[gate_id]
        for gate in self.circuit.G.values():
            # evaluate output gates
            if gate.is_circuit_output :
                """ @student
                evaluate_garbled_gate() has no return value (and it is not suppose to have one)
                """
                evaluate_garbled_gate(gate)
                circuit_outputs[gate.gate_id] = gate.output_value#evaluate_garbled_gate(gate)
        ##### Complete here #####
        #
        # evaluate the garbled circuit here and store the result for the output gates in circuit_outputs
        #
        #####

        return circuit_outputs


    def oblivious_transfer(self,garbler):
        my_input_keys = {}
        for i in self.myinputs:
            c = garbler.oblivious_transfer(i,self.OT_receiver.challenge(self.myinputs[i]),self.OT_receiver.pk)
            my_input_keys[i] = self.OT_receiver.decrypt_response(c[0],c[1],self.myinputs[i])

        ##### Complete here #####
        #
        # for each of my inputs, retrieve the corresponding key by engaging an OT with the garbler
        #
        #####
        return my_input_keys

def test_garbled_circuit():
    Alice = garbler(PRS_circuit,{'igate_A':None,'igate_B':None}) # Alice's inputs are A,B chosen randomly
    garbled_table = Alice.garble()
    Bob_choice = None
    while Bob_choice not in ['PAPER','ROCK','SCISSORS','LOSE','P','R','S','L'] :
        Bob_choice = input( 'Bob\'choice is PAPER (P), ROCK (R), SCISSORS (S) or LOSE (L) : ')
    C,D = choice_to_bin(Bob_choice)
    OT_receiver = OT.Receiver()
    Bob = evaluator(PRS_circuit,{'igate_C':C,'igate_D':D},OT_receiver) # Bob's inputs are C,D chosen by user

    Alice_input_keys = Alice.input_keys() # @student: Why this does not reveal the inputs of Alice to Bob ?
    Bob_input_keys = Bob.oblivious_transfer(Alice) # @student: Why this does not reveal the inputs of Bob to Alice ?
    circuit_outputs = Bob.evaluate(garbled_table, Bob_input_keys, Alice_input_keys)
    print(result(circuit_outputs['gate_E'],circuit_outputs['gate_F']))


def choice_to_bin(choice):
    if choice in ['PAPER','P']:
        return 0,0
    elif choice in ['ROCK','R']:
        return 1,0
    elif choice in ['SCISSORS', 'S']:
        return 0,1
    elif choice in ['LOSE','L']:
        return 1,1

def result(E,F):
    if E == 0 :
        if F == 0 :
            return 'draw'
        else :
            return 'Bob wins'
    else :
        return 'Alice wins'

test_garbled_circuit()
