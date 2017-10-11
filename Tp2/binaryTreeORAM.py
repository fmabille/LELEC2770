# -*- coding: utf-8 -*-
"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : ORAM

Bynary tree ORAM
"""

import random

Memory = ["a","b","c","d"]
pos = {}
pos_number = {}
s_bucket = 4

class Node:
    def __init__(self):
        self.level = 0
        self.parent = []
        self.child = []
        self.bucket = []
        self.bucket_index = []
        self.name = 0

    def __str__(self):
        return 'Node'+str(self.name)+'with bucket'+str(self.bucket)

class Tree:
    def __init__(self,nbr_level=2):
        self.tree_level = nbr_level
        self.list_node = []
        nbr_node = 0
        lvl = 1
        self.list_node.append(Node())
        nbr_node += 1
        self.list_node[0].name = nbr_node
        while lvl <= nbr_level:
            dim = len(self.list_node)
            for i in range(dim):
                if self.list_node[i].level == lvl - 1:
                    node_1 = Node()
                    node_1.level = lvl
                    node_1.parent = self.list_node[i]
                    nbr_node += 1
                    node_1.name = nbr_node
                    self.list_node.append(node_1)

                    node_2 = Node()
                    node_2.level = lvl
                    node_2.parent = self.list_node[i]
                    nbr_node += 1
                    node_2.name = nbr_node
                    self.list_node.append(node_2)

                    self.list_node[i].child = [node_1, node_2]
            lvl += 1

        self.list_leaf = []
        for i in range(len(self.list_node)):
            if self.list_node[i].level == self.tree_level:
                self.list_leaf.append(self.list_node[i])

        for i in range(len(Memory)):
            assign = False
            while assign == False:
                index_leaf = random.randrange(0,len(self.list_leaf))
                if len(self.list_leaf[index_leaf].bucket) < s_bucket:
                    assign = True
            self.list_leaf[index_leaf].bucket.append(Memory[i])
            self.list_leaf[index_leaf].bucket_index.append(i)
            pos[i] = self.list_leaf[index_leaf]

    def __str__(self):
        s = ''
        for node in self.list_node :
            s += str(node)+' \n '
        return s

    def computePath(self,node):
        path = []
        path.append(node)
        lvl = self.tree_level
        while lvl >= 0:
            path.append(path[len(path)-1].parent)
            lvl -= 1
        path.pop()
        return path

    def query(self,addr):
        path = self.computePath(pos[addr])
        for i in range(len(path)):
            if len(path[i].bucket) > 0:
                dim = len(path[i].bucket)
                for j in range(dim):
                    if path[i].bucket_index[j] == addr:
                        m = path[i].bucket[j]
                        if path[i].level != 0 :
                            path[i].bucket_index.remove(addr)
                            path[-1].bucket_index.append(addr) # add block address to root node
                            path[i].bucket.remove(m)
                            path[-1].bucket.append(m) # add block to root node
                        else :
                            pass
                        break
        del pos[addr]
        index_leaf = random.randrange(0,len(self.list_leaf))
        pos[addr] = self.list_leaf[index_leaf]

        self.evict()

        return m

    @staticmethod
    def two_random_node(level):
        n = random.randint(0,2**level-1)
        n2 = random.randint(0,2**level-1)
        while(n == n2):
            n2 = random.randint(0,2**level-1)
        return n, n2


    def evict(self, level):
        #
        if level == 0:
            node = self.list_node[level]
            for i in node.bucket:

        else:
            n,n1 = two_random_node(level)

        self.evict(level+1)
