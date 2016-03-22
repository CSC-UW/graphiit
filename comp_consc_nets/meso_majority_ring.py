import pyphi
import numpy as np

# Analyze the effect of micro cuts on the MESO scale network


Nodes = 14
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    if (ps[10] == 1 and ps[11] == 1):
        cs[0] = 1
    if (ps[10] == 1 and ps[12] == 1):
        cs[1] = 1
    if (ps[11] == 1 and ps[12] == 1):
        cs[2] = 1
    cs[10] = 0.5
    cs[11] = 0.5
    cs[12] = 0.5
    cs[13] = 0.5
    if (ps[0] == 1 or ps[1] == 1 or ps[2] == 1):
        cs[3] = 1
    if (ps[3] == 1 and ps[10] == 1):
        cs[6] = 1
        cs[9] = 1
    if (ps[3] == 1 and ps[11] == 1):
        cs[8] = 1
    if (ps[3] == 1 and ps[12] == 1):
        cs[4] = 1
    if (ps[3] == 1 and ps[13] == 1):
        cs[5] = 1
        cs[7] = 1
    tpm[psi, :] = cs

cm = np.array([
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

cOR = sub.concept((sub.nodes[3],))
cAND1 = sub.concept((sub.nodes[0],))
cAND2 = sub.concept((sub.nodes[1],))
cAND3 = sub.concept((sub.nodes[2],))



# cut 0 to 6

# The AND concept moves 0.5, its varphi is 0.125
# The OR concept moves 0.25 and its varphi is 0.071429
# Phi = 0.08035

Nodes = 14
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    if (ps[11] == 1):
        cs[0] = 0.5
    if (ps[10] == 1 and ps[12] == 1):
        cs[1] = 1
    if (ps[11] == 1 and ps[12] == 1):
        cs[2] = 1
    cs[10] = 0.5
    cs[11] = 0.5
    cs[12] = 0.5
    cs[13] = 0.5
    if (ps[0] == 1 or ps[1] == 1 or ps[2] == 1):
        cs[3] = 1
    if (ps[3] == 1 and ps[10] == 1):
        cs[9] = 1
    if (ps[10] == 1):
        cs[6] = 1
    if (ps[3] == 1 and ps[11] == 1):
        cs[8] = 1
    if (ps[3] == 1 and ps[12] == 1):
        cs[4] = 1
    if (ps[3] == 1 and ps[13] == 1):
        cs[5] = 1
        cs[7] = 1
    tpm[psi, :] = cs

cm = np.array([
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub2 = pyphi.Subsystem(range(net.size), net)






# cut 6 to 9

# The AND concept is destroyed (moves 1.125 its varphi is 0.125)
# The OR concept moves 0.071429 and its varphi is 0.071429
# Phi = 0.1457

Nodes = 14
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    if (ps[10] == 1 and ps[11] == 1):
        cs[0] = 1
    if (ps[10] == 1 and ps[12] == 1):
        cs[1] = 1
    if (ps[11] == 1 and ps[12] == 1):
        cs[2] = 1
    cs[10] = 0.5
    cs[11] = 0.5
    cs[12] = 0.5
    cs[13] = 0.5
    if (ps[1] == 1 or ps[2] == 1):
        cs[3] = 1
    else:
        cs[3] = 0.5
    if (ps[3] == 1 and ps[10] == 1):
        cs[6] = 1
        cs[9] = 1
    if (ps[3] == 1 and ps[11] == 1):
        cs[8] = 1
    if (ps[3] == 1 and ps[12] == 1):
        cs[4] = 1
    if (ps[3] == 1 and ps[13] == 1):
        cs[5] = 1
        cs[7] = 1
    tpm[psi, :] = cs

cm = np.array([
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub2 = pyphi.Subsystem(range(net.size), net)

