from thisfiles import *

def pointerdist(P, accumulator=dict(ptrf=0,ptd=0)):
    for u in P.keys():
        for v, direction in P[u]:
            if direction == '>':
                x, y = u, v
            else:
                x, y = v, u
            if isinstance(v, RegularFile):
                accumulator['ptrf'] += 1
            elif isinstance(v, Directory):
                accumulator['ptd'] += 1
    return accumulator

def mean(l):
    return sum(l) / len(l)

def std(l, m=None):
    if m is None:
        m = mean(l)
    return (sum((x - m)**2 for x in l) / len(l))**(0.5)

def mean_std(l):
    m = mean(l)
    s = std(l, m)
    return m, s
