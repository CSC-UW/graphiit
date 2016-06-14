# Lambdas avoided for easier debugging


def AND(inputs):
    return sum(inputs) == len(inputs)


def NAND(inputs):
    return not AND(inputs)


def OR(inputs):
    return sum(inputs) >= 1


def COPY(inputs):
    assert len(inputs) <= 1, "COPY gates cannot have multiple inputs"
    return OR(inputs)


def NOR(inputs):
    return not OR(inputs)


def NOT(inputs):
    assert len(inputs) <= 1, "NOT gates cannot have multiple inputs"
    return NOR(inputs)


def XOR(inputs):
    return sum(inputs) % 2 == 1


def MAJORITY(inputs):
    return sum(inputs) > len(inputs)/2


def MAJ(inputs):
    return MAJORITY(inputs)


def MINORITY(inputs):
    return sum(inputs) <= len(inputs)/2


def MIN(inputs):
    return MINORITY(inputs)


def PARITY(inputs):
    return sum(inputs) % 2 == 0


def PAR(inputs):
    return PARITY(inputs)


MAP = {
    'AND': AND,
    'NAND': NAND,
    'OR': OR,
    'NOR': NOR,
    'COPY': COPY,
    'NOT': NOT,
    'XOR': XOR,
    'MAJORITY': MAJORITY,
    'MAJ': MAJ,
    'MINORITY': MINORITY,
    'MIN': MIN,
    'PARITY': PARITY,
    'PAR': PAR,
}
