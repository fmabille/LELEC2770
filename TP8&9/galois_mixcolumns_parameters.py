# use default parameters for the GF:
# (change the irreductible polynomial and field size here)
from ff import GF2int, init_lut
FIELD_EXPONENT = 4
init_lut(generator=3, prim=0x16, c_exp=FIELD_EXPONENT)

