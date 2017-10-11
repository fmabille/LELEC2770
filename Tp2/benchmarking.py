from pathORAM import PathORAMTree, PathORAM
import matplotlib.pyplot as plt
from random import randint,sample

def benchmark(PathOram,n):
    clientStashSize = []

    t_mean = 0
    for i in range(n):
        PathOram.queryBlock()

    plt.plot(range(n), clientStashSize)
    plt.show()

    print t_mean/n, 'sec per query'



def createPathORAM(depth = 5,nbChildren = 4,nbWords = None):

    # create PO Tree
    po_tree = PathORAMTree(depth = depth , nbChildren = nbChildren , treeID = 'test_PO_tree')

    print 'theoretic load of the tree is ', po_tree.tLoad

    if nbWords ==  None :
        nbWords = int(po_tree.tLoad/4)

    print 'parameters are ', depth, nbChildren, nbWords

    def fbm():
        return randint(0,1000)

    po_tree.setup(fbm)

    PO = PathORAM(po_tree)

    print 'Path ORAM tree created'

    L = ['ba','be','bi','bo','bu','ca','ce','ci','co','cu','da','de','di','do','du','fa','fe','fi','fo','fu','ga','ge','gi','go','gu','ha','he','hi','ho','hu','ja','je','ji','jo','ju','ka','ke','ki','ko','ku','la','le','li','lo','lu','ma','me','mi','mo','mu','na','ne','ni','no','nu','pa','pe','pi','po','pu','ra','re','ri','ro','ru','sa','se','si','so','su','ta','te','ti','to','tu','va','ve','vi','vo','vu','wa','we','wi','wo','wu','xa','xe','xi','xo','xu','za','ze','zi','zo','zu']
    words  = []
    for i in range(nbWords):
        word = ''
        for j in range(8) :
            syllab = sample(L,1)[0]
            word += syllab
        words.append((i,word))

    print 'List of blocks generated'

    PO.fillupStash(words)# at the beggining the tree is empty and the stash is full

    print 'Stash filled'

    return PO

createPathORAM(7,5,6)
