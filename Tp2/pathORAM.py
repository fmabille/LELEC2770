# -*- coding: utf-8 -*-
"""
Created on 2017
Author : Edouard Cuvelier
Affiliation : Université catholique de Louvain - ICTEAM - UCL Crypto Group
Address : Place du Levant 3, 1348 Louvain-la-Neuve, BELGIUM

LELEC2770 : Privacy Enhancing Technologies

Exercice Session : ORAM

Path ORAM
"""

from Crypto.Random.random import randint
from random import sample
import time

NO_PRINT = False

class PathORAMTree :

    def __init__(self,root = None, bucketList = [], Z = 4, nbChildren = 2 ,depth = 10, treeHash = '', treeID=''):
        '''
        - root, the root of the tree
        - bucketList is the list of all the nodes of the tree
        - Z is the exact size of the bucket
        - nbChildren is the exact number of children a node must have except for
        the leaf nodes which have none and their parents which have only one
        - depth is the number of level of the tree
        - treeHash is the Merkle-Damgard hash of the tree
        - treeID is a string used to identify the tree
        '''
        self.root = root
        self.bucketList = bucketList
        self.Z = Z # exact number of blocks in each bucket
        self.nbChildren = nbChildren # exact number of children a bucket has
        self.depth = depth # of the tree
        self.treeID = treeID

        tLoad = Z
        st = 1
        for i in range(depth):
            st = st*nbChildren
            tLoad = tLoad + Z*st

        self.tLoad = tLoad

    def __str__(self):
        return 'Path ORAM Tree '+str(self.treeID)+' with root \n\t'+str(self.root)+'\n\t Z = '+str(self.Z)+'\n\t number of children = '+str(self.nbChildren)+'\n\t depth = '+str(self.depth)+'\n\t and bucket list : \n\t\t'+str(self.bucketList)

    def __repr__(self):
        return self.__str__()

    def setup(self,fillingBlockMethod):
        '''
        Build the PO tree by filling each node of the tree by buckets and by
        filling each bucket with self.Z blocks where a block is constructed using
        the fillingBlockMethod argument
        '''
        L = []
        for i in range(self.Z):
            L.append(fillingBlockMethod())

        root = PathORAMBucket(self,None,[],L,(0,0),isRoot=True)

        self.root = root
        self.bucketList.append(self.root)

        def createChildren(bucket, depth):
            if depth == 0 :
                leaf = PathORAMBucket(self,bucket,[],[],(bucket.position[0]+1,0),isLeaf=True)
                bucket.children = [leaf]
                self.bucketList.append(leaf)

            else :
                childrenList = []
                for i in range(self.nbChildren):
                    L = []
                    for j in range(self.Z):
                        L.append(fillingBlockMethod())

                    childrenList.append(PathORAMBucket(self,bucket,[],L,(bucket.position[0]+1,i)))

                bucket.children = childrenList

                for child in childrenList :
                    self.bucketList.append(child)
                    createChildren(child,depth-1)

        createChildren(self.root,self.depth)


    def isEmpty(self):
        if self.bucketList == [] :
            assert self.root == None
            return True
        else :
            return False


class PathORAMBucket :

    def __init__(self,POTree,parent,children,blockList, position, subTreeHash=None, isRoot=False,isLeaf=False):
        '''
        - POTree is the Path ORAM tree in which the bucket is
        - parent is the parent node of the bucket
        - children is a list containing the children nodes of bucket
        - blockList is a list containing the blocks stored in the bucket its size
        is exaclty POTree.Z
        - position is a pair of int (x,y) where
            - x is the level of the bucket
            - y is the (unique) order among the other siblings
        - subTreeHash is the hash of the sub tree of which bucket is the root
        - isRoot is a boolean whose meaning is obvious
        - isLeaf is a boolean whose meaning is obvious
        '''
        self.POTree = POTree
        self.parent = parent
        self.children = children
        self.blockList = blockList
        self.position = position
        self.subTreeHash = subTreeHash # MD hash of the subtree whose root is self
        self.isRoot = isRoot
        self.isLeaf = isLeaf

        if self.isRoot :
            assert self.parent == None
            assert self.isLeaf is False
            self.idNumber = '0'
        else :
            self.idNumber = self.parent.idNumber + str(self.position[1])

        if self.isLeaf :
            assert self.children == []
            assert self.blockList == []
            assert self.isRoot is False
            assert self.parent != None

    def __str__(self):
        if self.isRoot :
            return 'Root Bucket of the PO tree '+self.POTree.treeID

        elif self.isLeaf :
            return 'Leaf Bucket '+str(self.idNumber) +' of the PO tree '+self.POTree.treeID
        else :
            return 'PO Bucket '+str(self.idNumber) +' of the PO tree '+self.POTree.treeID

    def __repr__(self):
        return self.__str__()

    def merkleDamgardHash(self):
        return None

class PathORAM :

    def __init__(self,POTree, creatDummyBlock = None, rerandomizeBlock = None):
        '''
        - POTree is the Path ORAM tree in which the data will be stored

        The ethod initialize the folowing variables:
        - positionDic is a dictionnary used to store the position in which a block
        is currently stored, an item of the dictionnary is of the form
        {bucketID : [(blockID,path),...,] of size Z} ; bucketID is set to 'stash', when the
        block is stored in the client Stash, in this cas blockID is set to None
        - positionMap is a dictionary of the form {blockID : (bucketID,path)}
        - clientStash is a dictionary { blockID : block } where
        path is the path on which some blocks must be stored
        '''
        self.POTree = POTree
        self.positionDic = {'stash':[]} # stores entries of the form {bucketID : [(blockID,path),...,] of size Z}
        self.positionMap = {} # stores entires of the form {blockID : (bucketID,path)}
        self.clientStash = {} # stores entires of the form {blockID : block }
        self.pathList = self.buildPathList()

        for node in self.POTree.bucketList : # follow the path from leaf to root
            nodeID = node.idNumber
            if not len(nodeID) ==  self.POTree.depth + 2 :
                # is not a leaf
                self.positionDic[nodeID] = [('','')]*self.POTree.Z

        if creatDummyBlock == None :
            def f():
                return 'dummy block'
            self.createDummyBlock = f
        else :
            self.createDummyBlock = creatDummyBlock

        if rerandomizeBlock == None :
            def fb(block):
                return ('rerand', block)
            self.rerandomizeBlock = fb
        else :
            self.rerandomizeBlock = rerandomizeBlock

    def buildPathList(self):
        '''
        this method returns an iterable of the path of self.POTree
        A path is a string of the form '025103...40' where a letter x at index i
        indicates that the child x of the previous node of level i-1 is in the
        path. The first letter is 0, for the root and the last is always 0 for a
        leaf.
        '''

        def genWords(alphabet,length):
            '''
            alphabet is a list of string
            '''
            if length == 1 :
                return alphabet
            else :
                new_words = []
                words = genWords(alphabet,length-1)
                for word in words :
                    for letter in alphabet :
                        new_words.append(letter+word)

                return new_words

        alphabet  = []
        for i in range(self.POTree.nbChildren):
            alphabet.append(str(i))

        paths = genWords(alphabet,self.POTree.depth)
        pathList = []
        for path in paths :
            pathList.append('0'+path)
        return pathList

    def fillupStash(self,blockList):
        '''
        Given a blockList (of the form blockId, block = blockList[i]), this
        method fills up the self.clientStash and attributes uniformly randomly
        a path to each block. The method also sets up the self.positionDic
        '''
        n = len(self.pathList)

        assert self.positionDic['stash'] == [] # Stash is not empty do not use this method!


        for i in range(len(blockList)):
            blockID, block = blockList[i]
            r = randint(0,n-1)
            path = self.pathList[r]

            self.positionDic['stash'].append((blockID,path))
            self.positionMap[blockID] = ('stash',path)
            self.clientStash[blockID] = block

    def randomlyAssignStash(self):
        '''
        This method randomly assign each block of the stash into the PO Tree.
        For this method to work, the PO tree must contain enough empty spaces!
        '''
        stash_copy = self.clientStash.copy()
        bucketList = self.positionDic.keys()
        bucketList.remove('stash')
        for blockID in stash_copy :
            bucketID,path = self.positionMap[blockID]
            assert bucketID == 'stash'
            assert (blockID,path) in self.positionDic['stash']
            # reassign block
            cond = True
            nbTries = 0
            while cond :
                if nbTries > 1000 :
                    print 'the number of tries exceed 1000, the method stops'
                    return
                r = randint(0, len(bucketList)-1)
                randomBucketID = bucketList[r]
                if ('', '') in self.positionDic[randomBucketID] :
                    # there is one empty block in the bucket
                    i = self.positionDic[randomBucketID].index(('',''))
                    self.clientStash.pop(blockID)
                    self.positionDic[randomBucketID][i] = (blockID,path)
                    self.positionMap[blockID] = (randomBucketID,path)
                    cond = False

                nbTries += 1



    def queryBlock(self,blockID):
        '''
        This method returns a block whose Id is blockID. Doing so, the method
        changes all the buckets (and blocks) that are on the path of the block.
        Also the self.clientStash, the self.positionDic and the self.positionMap
        are modified at the end of the execution.
        '''
        Z = self.POTree.Z
        lstash0 = len(self.clientStash)

        bucketID,path = self.positionMap[blockID]

        n = len(self.pathList)
        r = randint(0,n-1)
        new_path = self.pathList[r] # Chose a new location for the querried block
        print 'Querrying block ', blockID, ' stored on path ', path, ', the block is reassigned to ',new_path


        if bucketID == 'stash':
            # the block is stored in the stash
            queriedBlock = self.clientStash[blockID]

            for i in range(len(self.positionDic['stash'])):
                if self.positionDic['stash'][i][0] == blockID :
                    blockOrder = i
                    break

            self.positionDic['stash'][blockOrder] = (blockID,new_path) # update positionDic accordingly
            self.positionMap[blockID] = ('stash',new_path)  # update positionMap accordingly

        node = self.POTree.root
        path_copy = path[1:]+'0'
        bucketList = [] # bucketList will be used afterwards to rewrite blocks into the tree
        dummyblockList = []

        while not node.isLeaf :

            for i in range(Z) :

                block_i = node.blockList[i]
                block_i_ID, block_i_path = self.positionDic[node.idNumber][i]

                if (block_i_ID, block_i_path) != ('', '') :
                    # the block i is not a dummy block
                    assert not block_i_ID in self.clientStash
                    self.clientStash[block_i_ID] = block_i # add the block to the stash
                    if bucketID == node.idNumber and blockID == self.positionDic[bucketID][i][0]:
                        # this is the block we seek (it is not stored in the stash)
                        queriedBlock = node.blockList[i]
                        self.positionDic['stash'].append((blockID,new_path)) # update positionDic accordingly
                        self.positionMap[blockID] = ('stash',new_path)  # update positionMap accordingly

                    else :
                        self.positionDic['stash'].append((block_i_ID,block_i_path)) # update positionDic accordingly
                        self.positionMap[block_i_ID] = ('stash',block_i_path) # update positionMap accordingly

                else :
                    # This is a dummy block, we have to fake its retrieval
                    #TODO: fake retrieval
                    dummyblockList.append('dummy block')

            bucketList = [node] +bucketList

            a = path_copy[0]
            path_copy = path_copy[1:] # remove first letter of path_copy
            node = node.children[int(a)]

        def getCandidates(BuID):
            '''
            Check in the clientStash if there are candidates blocks that could be
            stored in this bucket (with BuID identifier)
            Return a list of candidates
            '''
            n = len(BuID)
            candidatesList = []
            L = self.positionDic['stash']
            for bloID,path in L :
                if path[:n] == BuID :
                    candidatesList.append(bloID)
            return candidatesList

        lstash1 = len(self.clientStash)
        for bucket in bucketList : # follow the path from leaf to root
            nodeID = bucket.idNumber
            candidates = getCandidates(nodeID)

            if len(candidates)< Z :
                for i in range(Z-len(candidates)):
                    if len(dummyblockList)>0 :
                        candidates.append(dummyblockList.pop(0))
                    else :
                        print '! Creation of new dummy block !'
                        candidates.append('new DB')

            for i in range(Z):
                # here we store the candidates blocks (previously stored in the stash) into the bucket
                bloID = candidates[i]
                if not bloID == 'new DB' and not bloID == 'dummy block' :
                    buID, bloPath = self.positionMap[bloID]
                    assert buID == 'stash'
                    block = self.clientStash[bloID]
                    rerand_block = self.rerandomizeBlock(block)
                    bucket.blockList[i] = rerand_block
                    # update the class variable accordingly of the new position of the block
                    self.clientStash.pop(bloID)
                    self.positionDic['stash'].remove((bloID,bloPath)) # remove it from the stash
                    self.positionDic[nodeID][i] = bloID,bloPath
                    self.positionMap[bloID] = nodeID, bloPath
                elif bloID == 'dummy block' :
                    #rerand_block = self.rerandomizeBlock(dummyBlock)
                    bucket.blockList[i] = self.createDummyBlock()
                    self.positionDic[nodeID][i] = ('','')
                else :
                    bucket.blockList[i] = self.createDummyBlock()
                    self.positionDic[nodeID][i] = ('','')


        lstash2 = len(self.clientStash)
        if not dummyblockList == []:
            print 'dummyblock list is not empty !'
            for dummyBlock in dummyblockList :
                self.rerandomizeBlock(dummyBlock)
        if not NO_PRINT :
            print 'Size of the client stash before, after lookup, and after refilling tree: ', lstash0,lstash1,lstash2

        return queriedBlock
