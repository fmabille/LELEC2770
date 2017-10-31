# -*- coding: utf-8 -*-
"""
LELEC2770 : Privacy Enhancing Technologies

Exercice Session : Voting
"""

''' Library needed for the Oblivious Transfer '''


import gmpy
from Crypto.Random.random import randint
from Crypto.Hash import SHA256
import httplib, json



def get_bulletin_board(full_url):
    """
        full_url must be https://[domain]/[GET_PARAM]

        returns a dictionary containing
        'p'
        'q'
        'g'
        'h'
        'ciphertexts'
    """
    domain = full_url.split('/')[2]
    conn = httplib.HTTPSConnection(domain)
    get_param = "/"
    for elem in full_url.split('/')[3:]:
        get_param += elem+"/"
    conn.request("GET", get_param)
    r = conn.getresponse()
    if r.status >= 400:
        print r.status, r.reason
        json_val = ""
    else:
        json_val = r.read()
    conn.close()
    return json.loads(json_val)


def El_Gamal_ParamGen():
    p = 4
    while not gmpy.is_prime(p):
        r = randint(0,2**64)
        q = gmpy.next_prime(2**64+r)
        p = 2*q+1
    g_prime = randint(1,int(p-1))
    g = pow(g_prime,2,p) # generator of the group
    assert pow(g,q,p) == 1
    G = g,p,q
    x = randint(1,int(q-1)) # secret key
    y = pow(g,x,p) # public key
    pk = El_Gamal_PublicKey(G,y)
    sk = El_Gamal_SecretKey(G,x)
    return pk,sk


class El_Gamal_PublicKey:
    def __init__(self,G,y):
        self.G = G
        self.y = y

    def random(self,bound=None):
        q = self.G[2]
        if bound == None :
            bound = q
        return randint(1,int(bound))

    def encrypt(self,m,r=None):
        if r == None:
            r = self.random()
        g = self.G[0]
        p = self.G[1]
        q = self.G[2]


        r = r%q
        m = m%q

        c1 = pow(g,r,p)
        c2 = (pow(g,m,p)*pow(self.y,r,p))%p


        return El_Gamal_Ciphertext(p,c1,c2)

    def verifiabilityProof(self,c,m,r,s=None,u=None,t=None):
        ''' This ZK proof ensures that c is a el_gamal on m = 0 or 1
        s,u,t are the randomness used in the proof (optional)
        '''
        # notations
        p = self.G[1]
        q = self.G[2]

        assert m==0 or m==1 # the proof works only if m = 0 or 1

        if s == None:
            s = self.random()
        if u == None:
            u = self.random()
        if t == None:
            t = self.random()

        if m == 0 :
            #commitment
            u1 = u
            t1 = t
            w0 = self.encrypt(0,s)
            w1 = self.encrypt(t1,u1-t1*r)
            # challenge
            h =self.hashf([self.G,self.y,c,w0,w1])
            t0 = (h-t1)%p
            # response
            u0 = (s+r*t0)%q
        else :
            # m == 1
            #commitment
            u0 = u
            t0 = t
            w0 = self.encrypt(-t0,u0-t0*r)
            w1 = self.encrypt(0,s)
            # challenge
            h =self.hashf([self.G,self.y,c,w0,w1])
            t1 = (h-t0)%p
            # response
            u1 = (s+r*t1)%q

        return [u0,u1,t0,t1]

    def verifiabilityProofCheck(self,c,proof):
        ''' Return True if the ZKP proof is correct with respect to c
        meaning that c is a el_gamal on either 0 or 1
        '''
        # notations
        c1 = c.c1
        c2 = c.c2
        p = self.G[1]
        g = self.G[0]
        y = self.y

        u0,u1,t0,t1 = proof

        u0g = pow(g,u0,p)
        t0c1 = pow(c1,t0,p)
        inv_t0c1 = gmpy.invert(t0c1,p)
        w0_1 = (u0g*inv_t0c1)%p

        u0y = pow(y,u0,p)
        t0c2 = pow(c2,t0,p)
        inv_t0c2 = gmpy.invert(t0c2,p)
        w0_2 = (u0y*inv_t0c2)%p
        w0 =  El_Gamal_Ciphertext(p,w0_1,w0_2)

        u1g = pow(g,u1,p)
        t1c1 = pow(c1,t1,p)
        inv_t1c1 = gmpy.invert(t1c1,p)
        w1_1 = (u1g*inv_t1c1)%p
        u1y = pow(y,u1,p)
        t1c2 = pow(c2,t1,p)
        inv_t1c2 = gmpy.invert(t1c2,p)
        t1g = pow(g,t1,p)
        w1_2 = (u1y*inv_t1c2*t1g)%p
        w1 =  El_Gamal_Ciphertext(p,w1_1,w1_2)

        h = self.hashf([self.G,self.y,c,w0,w1])

        return (t0+t1)%p == h

    def hashf(self,L):
        p = self.G[1]
        hash_f = SHA256.new()
        for obj in L :
            if type(obj) is tuple:
                for i in obj :
                    hash_f.update(str(i))
            elif obj is El_Gamal_Ciphertext :
                hash_f.update(str(obj.c1))
                hash_f.update(str(obj.c2))
            else :
                hash_f.update(str(obj))
        d = hash_f.digest()
        return int(d.encode('hex'),16)%p


class El_Gamal_SecretKey:

    def __init__(self,G,x):
        assert len(G) == 3, "G must be composed of g, p, q"
        self.G = G
        self.G = G
        self.x = x

    def decrypt(self,c):
        assert isinstance(c,El_Gamal_Ciphertext), "c does not seems to be a ciphertext"
        g = self.G[0]
        p = self.G[1]

        def dLog(g,g_m):
            a = 1
            i = 0
            while i<2**20:
                if a == g_m :
                    return i
                else :
                    a = a*g % p
                    i += 1
            return None # no DLog < 2**20 found

        c1 = c.c1
        c2 = c.c2
        c1_prime = pow(c1,self.x,p)
        g_m = gmpy.divm(c2,c1_prime,p)
        m = dLog(g,g_m)
        return m


class El_Gamal_Ciphertext:

    def __init__(self,p,c1,c2):
        self.p = p
        self.c1 = c1
        self.c2 = c2

    def __add__(self,other):
        return El_Gamal_Ciphertext(self.p,(self.c1*other.c1)%self.p,(self.c2*other.c2)%self.p)

    def __neg__(self):
        inv_c1 = gmpy.invert(self.c1,self.p)
        inv_c2 = gmpy.invert(self.c2,self.p)
        return El_Gamal_Ciphertext(self.p,inv_c1,inv_c2)

    def __sub__(self, other):
        return self.__add__(other.__neg__())

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, alpha):
        return El_Gamal_Ciphertext(self.p,pow(self.c1,alpha,self.p),pow(self.c2,alpha,self.p))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'El Gamal Ciphertext '+str(self.c1)+' , '+str(self.c2)




def compute():
    json = get_bulletin_board("https://lelec2770.pythonanywhere.com/elections1/static/votes1.json")
    pk = json["h"]
    p = json["p"]
    acc = None
    for i in json["ciphertexts"]:
        if acc is None:
            acc = El_Gamal_Ciphertext(p,i["c1"],i["c2"])
        else:
            acc += El_Gamal_Ciphertext(p,i["c1"],i["c2"])
    print(acc)

def get_first_voters():
    json = get_bulletin_board("https://lelec2770.pythonanywhere.com/elections1/static/votes1.json")
    y = json["h"]
    g = json["g"]
    p = json["p"]
    q = json["q"]
    G = (g,p,q)
    epk = El_Gamal_PublicKey(G,y)
    c = epk.encrypt(1)
    c0 = json["ciphertexts"][0]
    el = El_Gamal_Ciphertext(p,c0["c1"],c0["c2"])
    print(c+el)

#513 is the number of vote of the candidate --> see compute LOOL
#we can encrypt 0 and then we have the result of the voters 1 ----> see get_first_voters
