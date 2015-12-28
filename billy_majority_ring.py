# Recreate the concepts corresponding to micro nodes 6 and 9
# Such a cut is always available for the micro system
# The small-phi values and distance from the null concept define the big-phi
# value for a system when this cut is made.
# Since it is always an option, this gives an upper bound on Phi.

# In the all OFF case, if the subsystem is a cycle of NOR gates: Phi = 1


import pyphi
import numpy as np


# In the all ON scenario, all nodes must be included, because freezing a node ON would kill the causal link

Nodes = 7
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[4] = 0.5
    cs[5] = 0.5
    cs[6] = 0.5
    if (ps[0] == 0 and ps[4] == 0):
        cs[1] = 1
    if (ps[1] == 0 and ps[5] == 0 and ps[6] == 0):
        cs[2] = 1
    if (ps[2] == 0):
        cs[3] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c1 = sub.concept((sub.nodes[1],))

c1.phi
pyphi.compute.concept_distance(c1, sub.null_concept)

c2 = sub.concept((sub.nodes[2],))

c2.phi
pyphi.compute.concept_distance(c2, sub.null_concept)



# The different kinds of concepts for the micro


# 0, 1, 2, 3, 4, 5
# varphi = 0.25

Nodes = 5
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[1] = 0.5
    cs[3] = 0.5
    if (ps[0] == 0 and ps[1] == 0):
        cs[2] = 1
    if (ps[2] == 0 and ps[3] == 0):
        cs[4] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c = sub.concept((sub.nodes[2],))



# 6, 7, 8
# varphi = 0.125

Nodes = 6
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[1] = 0.5
    cs[3] = 0.5
    cs[4] = 0.5
    if (ps[0] == 0 and ps[1] == 0):
        cs[2] = 1
    if (ps[2] == 0 and ps[3] == 0 and ps[4] == 0):
        cs[5] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c = sub.concept((sub.nodes[2],))


# 9
# varphi = 0.5

Nodes = 5
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[1] = 0.5
    cs[2] = 0.5
    if (ps[0] == 0 and ps[1] == 0 and ps[2] == 0):
        cs[3] = 1
    if (ps[3] == 0):
        cs[4] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c = sub.concept((sub.nodes[3],))


# 10
#  varphi = 0.25

Nodes = 12
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[8] = 0.5
    cs[9] = 0.5
    cs[10] = 0.5
    cs[11] = 0.5
    if (ps[0] == 0):
        cs[1] = 1
    if (ps[1] == 0 and ps[10] == 0):
        cs[2] = 1
    if (ps[1] == 0 and ps[11] == 0):
        cs[3] = 1
        cs[5] = 1
    if (ps[1] == 0 and ps[8] == 0):
        cs[4] = 1
        cs[7] = 1
    if (ps[1] == 0 and ps[9] == 0):
        cs[6] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c = sub.concept((sub.nodes[1],))

# In total, there are
# 5 * (0.25 + 0.5 + 3*0.125 + 6*0.25) = 13.125 varphi


Nodes = 8
States = 2**Nodes

tpm = np.zeros((States, Nodes))

for psi in range(States):
    ps = tuple(map(int, bin(psi)[2:].zfill(Nodes)[::-1]))
    cs = [0 for i in range(Nodes)]
    cs[0] = 0.5
    cs[1] = 0.5
    cs[3] = 0.5
    cs[5] = 0.5
    cs[6] = 0.5
    if (ps[0] == 0 and ps[1] == 0):
        cs[2] = 1
    if (ps[2] == 0 and ps[3] == 0):
        cs[4] = 1
    if (ps[4] == 0 and ps[5] == 0 and ps[6] == 0):
        cs[7] = 1
    tpm[psi,:] = cs

cm = np.array([
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
])

cs = (1, 1, 1, 1, 1, 1, 1, 1)

net = pyphi.Network(tpm, cs, connectivity_matrix=cm)
sub = pyphi.Subsystem(range(net.size), net)

c1 = sub.concept((sub.nodes[2],))

c2 = sub.concept((sub.nodes[4],))



