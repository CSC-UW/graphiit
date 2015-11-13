# TODO: Implement RANDOM

AND = lambda xs: sum(xs) == len(xs)
NAND = lambda xs: not AND(xs)
OR = lambda xs: sum(xs) >= 1
NOR = lambda xs: not OR(xs)
XOR = lambda xs: sum(xs) % 2 == 1
MAJORITY = lambda xs: sum(xs) > len(xs)/2
MINORITY = lambda xs: sum(xs) <= len(xs)/2
PARITY = lambda xs: sum(xs) % 2 == 0
GREATER_THAN = lambda threshold: lambda xs: sum(xs) >= threshold
LESS_THAN = lambda threshold: lambda xs: sum(xs) < threshold
NULL = lambda _: False

def COPY(xs):
    assert len(xs) <= 1, "COPY gates cannot have multiple inputs"
    return OR(xs)

def NOT(xs):
    assert len(xs) <= 1, "NOT gates cannot have multiple inputs"
    return NOR(xs)
