import httplib
import hashlib
import json
import time
from struct import pack, unpack
import random
import requests
import pdb
import argparse

parser = argparse.ArgumentParser(description="Some dummy miner for fun")
parser.add_argument("--print_stickman", action="store_true")

_TEST = False
DIFFICULTY = 25

####
# CHANGE YOUR NAME HERE TO SOMETHING UNIQUE!
MY_NAME = "DonalD Trump"

if _TEST:
    NODE_URL = "http://localhost:8000"
else:
    NODE_URL = "https://lelec2770.pythonanywhere.com"

"""
    We have left lots of opportunities for optimization.
    credit will be awarded for mining a block that adds to the main chain
    (20 FabulousCoins). Note that the faster you solve the proof of work,
    the better your chances are of landing in the main chain.

    Feel free to modify this code in any way

    /!\ chains with unvalid blocks will be discarded by the server at the
    end of the game /!\
    /!\ A chain is valid only if it contains valid blocks /!\
    /!\ A block is valid if it contains a valid dancemove and if
        its header_hash == Hash(nonce || previous_block) /!\

    /!\ Difficulty 21 bits, secret is 4 bits ! /!\
    Good luck!
"""

class State:

    def __init__(self, secret='', size=0):
        self.secret = secret
        self.size= size

    def __str__(self):
        return self.secret

    def __repr__(self):
        return self.secret


    def get_size(self):
        return self.size

    def successor(self):
        lst = []
        if self.size == 4:
            return lst

        s1 = State(self.secret + "0", self.size+1)
        s2 = State(self.secret + "1", self.size+1)

        lst.append(s1)
        lst.append(s2)

        return lst


class BruteForce:

    def __init__(self):
        self.stack = []
        self.stack.append(State())


    def put_next(self, iterator):
        for state in iterator:
            self.stack.append(state)

    def next_candidate(self):

        while len(self.stack) != 0:
            ret = self.stack.pop()
            self.put_next(ret.successor())
            if ret.get_size() == 4:
                return ret

        raise Exception


bf = BruteForce()




def solve_block(b, pb):
    """
    Iterate over random nonces until a valid proof of work is found
    for the block

    Expects a blocks dictionary `b` `pb` with id, parent_id,
    nonce, dancemove, miner_name as dictionary keys.

    """
    b["nonce"] = rand_nonce(DIFFICULTY)
    while True:
        b["nonce"] += 1
        hh = hash_block_to_hex(b, pb)
        # TODO: verify PoW

        a = "000000000000000000000" + str(bf.next_candidate())

        b["hash_header"] = hh
        return



def main():
    """
    Repeatedly request all blocks from the server, then build the blockchain
    then choose the right chain to start mining the next block

    We will construct a block dictionary and pass this around to solving and
    submission functions.
    """

    #/!\ This is an example ! Feel free to do another strategy ! /!\
    while True:
        #   Next block's parent, version, difficulty
        blocks = get_blocks()
        #   From all blocks received from the server, reconstruct the blockchain
        blockchains = reconstruct_blockchain(blocks)
        #   Choose the right block from the blockchain: TODO
        choosen_block = choose_chain(blockchains)[-1]
        #   Construct a block with our name in the contents that appends to the
        #   head of the main chain
        new_block = make_block(choosen_block)
        #   Solve the POW
        response = {}
        while "success" not in response:
            print "Solving block..."
            print new_block
            solve_block(new_block, choosen_block)
            response = suggest_block(new_block)
            print response
        #   Send to the server
        add_block(new_block)

def choose_chain(blockchains):
    """
    Expect one or several blockchains composed
    of a list of blocks

    return the choosen chain
    """
    # /!\ you might want to do something else.. :)
    choosen_chain = []
    maxv = 0
    for chain in blockchains:
        if maxv < len(blockchains[chain]):
            choosen_chain = blockchains[chain]
            maxv = len(blockchains[chain])
    return choosen_chain

def reconstruct_blockchain(blocks):
    """
    Expect to receive a list of blocks.

    Output {"0": [...], "1": [...]}
    for n chains reconstructed
    """
    # /!\ You might want to do something else :)
    chain = {0:[]}
    for block in blocks:
        chain[0].append(block)
    return chain

def get_blocks():
    """
       Parse JSON of all block info
           [{'id':,
             'miner_name':,
             'parent_id':,
             'nonce':,
             'dancemove':,}, {...}, ...]
    """
    response = requests.get(NODE_URL+"/blockchain/blocks/get.json")
    return json.loads(response.text)['blocks']

def add_block(block):
    """
       Send JSON of solved block to server.
            block:
                parent_id
                miner_name
                nonce
                dancemove
       return {"success": message} if add to datase
       or {"error": message} if something bad happened
    """
    print "Sending a valid block to server"
    params = {'block_val':block}
    headers = {'content-type': 'application/json'}
    response = requests.post(NODE_URL+"/blockchain/blocks/add_block.json", data=json.dumps(params), headers=headers)
    return response.json()['answer']

def suggest_block(block):
    """
       Send JSON of solved block to server.
            block:
                parent_id
                miner_name
                nonce
                dancemove
       return an error in the form of a dictionnary:
       {"error":message}
            => message might be about correctness of your block
            => message might be about your guess of the secret regarding
               this block (answer higher or smaller)
       or
       {"success": message} if block is valid
       /!\ block is not added to the server's database. Use
       add_block to do that /!\
    """
    print "Suggesting a block to server..."
    params = {'block_val':block}
    headers = {'content-type': 'application/json'}

    response = requests.post(NODE_URL+"/blockchain/blocks/suggest_block.json", data=json.dumps(params), headers=headers)
    return response.json()['answer']

def hash_block_to_hex(b, pb):
    """
    Computes the hex-encoded hash of a block header. First builds an array of
    bytes with the correct endianness and length for each arguments. Then hashes
    the concatenation of these bytes and encodes to hexidecimal.
    """
    packed_data = []
    packed_data.extend(str(b["nonce"]))
    packed_data.extend(str(pb["hash_header"]))
    if pb['parent_id'] is not None:
        packed_data.extend(str(pb["parent_id"]))
    packed_data.extend(pb["miner_name"])
    packed_data.extend(str(pb["nonce"]))
    packed_data.extend(str(pb['dancemove']))
    b["hash_header"] = hashlib.sha1(''.join(packed_data)).hexdigest()
    return b["hash_header"]

def hashhex_to_bin(hashhex):
    """
    Util function:
    Returns the bin-encoded hash of a hexdigest omitting the first zeroes
    due to int cast. => check lenght to pad with zeroes

    Question: How long should be a sha1 binary?
    """
    return str(bin(int(hashhex,16)))[2:]

def make_block(choosen_block):
    """
    Constructs a new block.
    """
    block = {
        "miner_name": MY_NAME,
        #   for now, root is hash of block contents (team name)
        "parent_id": choosen_block['id'],
        #   nanoseconds since unix epoch
        "nonce": None, #currently none. Next step is to found it
        "dancemove": choose_dancemove()
    }
    return block

def rand_nonce(diff):
    """
    Returns a random int in [0, 2**diff)
    """
    return random.randint(0,2**diff-1)

def print_dancing_stickman():
    all_blocks = get_blocks()
    assert(len(all_blocks) > 0), "Looks like there is no blocks on the server"
    blockchains = reconstruct_blockchain(all_blocks)
    blockchain = choose_chain(blockchains)
    blockchain.sort(key=lambda x: x['parent_id'])
    for block in blockchain:
        print block['miner_name']
        if block['dancemove'] == 0 :
            print    """    O
   /|\
    |
   / \ """
        elif block['dancemove'] == 1:
            print    """    O
    |---
    |
   / \ """
        elif block['dancemove'] == 2:

            print    """    O
 ---|
    |
   / \ """
        elif block['dancemove'] == 3:

            print    """   \ /
    |
   \|/
    O  """
        elif block['dancemove'] == 4:
            print    """    O/
   /|
    |
   / \ """
        elif block['dancemove'] == 5:
            print    """   \O
    |\
    |
   / \ """
        elif block['dancemove'] == 6:
            print    """   \O/
    |
    |
   / \ """
        elif block['dancemove'] == 7:
            print    """   \ /
    |
   \|
    O\  """
        elif block['dancemove'] == 8:

            print    """   \ /
    |
    |/
   /O  """
        elif block['dancemove'] == 9:

            print    """   \ /
    |
    |
   /O\ """
        elif block['dancemove'] == 10:

            print   """ <(^-^<) """
        else:
            raise ValueError('The blockchain contains unvalid dancemove!')


def choose_dancemove():
    """

        return the dancemove you choose for the next block
    """
    return random.randint(1,10)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.print_stickman:
        print_dancing_stickman()
    else:
        main()
