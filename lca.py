from env import DEVNULL
from thisfiles import *

def find_set(obj):
    "obj must support some attributes"
    if obj != obj.p:
        obj.p = find_set(obj.p)
    return obj.p

def make_set(obj):
    obj.p = obj
    obj.rank = 0

def link(x, y):
    if x.rank > y.rank:
        y.p = x
    else:
        x.p = y
        if x.rank == y.rank:
            y.rank += 1

def union(x, y):
    link(find_set(x), find_set(y))

def least_common_ancestor(u, P, accumulator=dict(qf=0,qb=0,b=0,vc=0,sda=0,ptd=0,ptrf=0), f=DEVNULL):
    # offline, see 21-3 of CLRS
    make_set(u)
    find_set(u).ancestor = u
    if isinstance(u, Directory):
        for c in u.children:
            least_common_ancestor(c, P, accumulator, f)
            union(u, c)
            find_set(u).ancestor = u
    u.visited = True
    try:
        for v, direction in P[u]:
            if v.visited:
                lca = find_set(v).ancestor
                if direction == '>':
                    x, y = u, v
                else:
                    x, y = v, u
                print('lca is', lca, file=f)
                if lca == x.parent and lca == y.parent:
                    print(x, y, 'same-directory alias', file=f)
                    accumulator['sda'] += 1
                elif lca == x.parent:
                    print(x, y, 'quasi-forward edge', file=f)
                    accumulator['qf'] += 1
                elif lca == x or lca == y:
                    print(x, y, 'back edge', file=f)
                    accumulator['b'] += 1
                elif lca == y.parent:
                    print(x, y, 'quasi-back edge', file=f)
                    accumulator['qb'] += 1
                else:
                    print(x, y, 'very cross edge', file=f)
                    accumulator['vc'] += 1


    except KeyError:
        pass

    return accumulator

