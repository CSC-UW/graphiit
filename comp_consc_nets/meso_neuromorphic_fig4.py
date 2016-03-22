# Analyze the effects of micro cuts on the BBX'd system

import pyphi
import numpy as np
import graphite as g
import fig4_conf

fig4 = g.Network(fig4_conf.net_conf, fig4_conf.state1)

Nodes = 3
States = 2**Nodes
cs = (1, 0, 0)

# =============================================================================
# Uncut system

uncut_net = pyphi.Network(fig4.tpm, fig4.connectivity_matrix)
uncut_sub = pyphi.Subsystem(uncut_net, cs, range(uncut_net.size))

OR = uncut_sub.concept((0,))
AND = uncut_sub.concept((1,))
XOR = uncut_sub.concept((2,))

uncut_const = pyphi.compute.constellation(uncut_sub)

# =============================================================================
# Cut BA in/out (BA_io)

# "tpm" is the TPM of the macro system AFTER cutting, raising, and conditioning.
tpm = np.array([
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, .5, 0, .5, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, .5, 0, .5],
    [0, 0, 0, 0, 0, .5, 0, .5],
    [0, .5, 0, .5, 0, 0, 0, 0]
])
cs = (1, 0, 0)
net = pyphi.Network(tpm, fig4.connectivity_matrix)
sub = pyphi.Subsystem(net, cs, range(net.size))
const = pyphi.compute.constellation(sub)

dist = pyphi.compute.constellation_distance(uncut_const, const)
import pdb; pdb.set_trace()

# AND cause changes purview, but phi_cause stays the same
# OR effect is destroyed.
# There are other higher order effects.
# dist = 1.10417

# =============================================================================
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

