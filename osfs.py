# TODO: would anything here be improved by asynchronous or multiprocessing?
# if you're just making system calls I don't think so because that's all managed by the kernel which is necessarily monolithic
# speed improvements are likely through writing a C program using stdio and other standard libraries

import os
import subprocess
from time import time
from stat import S_IMODE, S_IFMT,\
                 S_IFDIR, S_IFCHR, S_IFBLK, S_IFREG, S_IFIFO, S_IFLNK, S_IFSOCK 

DEVNULL = open(os.devnull, 'w')

class File():
    total_dir = dict()

    def __init__(self, parent, name, st):
        self.parent = parent
        self.name = name
        self.st = st
        self.__class__.total_dir[st.st_ino] = self

        # attributes used for LCA algorithm
        self.rank = None
        self.p = None
        self.ancestor = None
        self.visited = None

    def absolute(self):
        s = self.name
        v = self
        while v.parent is not None:
            s = v.parent.name + '/' + s
            v = v.parent
        return s

    def __str__(self):
        return str(type(self)).split('.')[-1].rstrip('\'>') + '-' + self.absolute()

class Directory(File):
    iter_order = 1
    def __init__(self, parent, name, st):
        super().__init__(parent, name, st)
        self.children = []
    def add_child(self, child):
        self.children.append(child)

class RegularFile(File):
    iter_order = 0
    pass

class SymLink(File):
    iter_order = 2
    def points_to(self):
        try:
            return File.total_dir[os.stat(self.absolute()).st_ino]
        except (KeyError, FileNotFoundError):
            return None

class Mount(File):
    pass

class BlockDevice(File):
    pass

class CharDevice(File):
    pass

class Socket(File):
    pass

factorydct = {
        S_IFDIR: Directory,
        S_IFREG: RegularFile,
        S_IFLNK: SymLink,
        S_IFBLK: BlockDevice,
        S_IFCHR: CharDevice,
        S_IFSOCK: Socket}

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

def dfs(root, accumulator=dict(n = 0,
                               curr_depth=0,
                               ndir=[],
                               nsym=[],
                               nrf=[],
                               nchild=[],
                               depths=[], 
                               hlinks=[],
                               subtree_sizes=[],
                               subtree_depths=[],
                               subtree_nested_depths=[]),
              P = dict(),
              f = DEVNULL):

    ndir = nsym = nrf = 0
    for child in sorted(root.children, key=lambda x:x.__class__.iter_order): # iterate through RegularFiles first
        print(child, file=f)
        accumulator['n'] += 1
        accumulator['depths'].append(accumulator['curr_depth'])
        if isinstance(child, Directory):
            ndir += 1
            accumulator['curr_depth'] += 1
            n0 = accumulator['n']
            l = len(accumulator['subtree_depths'])
            dfs(child, accumulator, P, f)
            accumulator['subtree_sizes'].append(accumulator['n'] - n0)
            accumulator['subtree_depths'].append(accumulator['curr_depth'])
            try:
                accumulator['subtree_nested_depths'].append(
                        mean([x - accumulator['curr_depth'] for x in accumulator['subtree_depths'][l:]]))
            except ZeroDivisionError:
                accumulator['subtree_nested_depths'].append(0)
                
            # if desired, include the child which branch is used for each balance
        elif isinstance(child, SymLink):
            nsym += 1
            pt = child.points_to()
            print(child, '->', pt, file=f)
            if pt is None:
                continue
            try:
                P[child].append( (pt, '>') )
            except KeyError:
                P[child] = [ (pt, '>') ]
            try:
                P[pt].append( (child, '<') )
            except KeyError:
                P[pt] = [ (child, '<') ]
        else: # RegularFile
            nrf += 1
            accumulator['hlinks'].append(child.st.st_nlink)

    accumulator['ndir'].append(ndir)
    accumulator['nsym'].append(nsym)
    accumulator['nrf'].append(nrf)
    accumulator['nchild'].append(ndir + nsym + nrf)
    
    accumulator['curr_depth'] -= 1

    return accumulator, P

def process(string_directory):
    # process to natural correspondence binary tree? would need to retain original parent designation
    dct = dict()
    root = Directory(None, string_directory, os.lstat(string_directory))
    dct[root.name] = root
    tstat = tcls = 0
    for r, s, f in os.walk(root.name, topdown=True):
        for i in s + f:
            fname = os.path.join(r, i)
            try:
                t0 = time()
                st = os.lstat(fname)
                tstat += time() - t0
            except FileNotFoundError:
                continue
            try:
                cls = factorydct[S_IFMT(st.st_mode)]
            except KeyError: # unsupported filetype
                continue
            t0 = time()
            ii = cls(dct[r], i, st)
            tcls += time() - t0
            dct[fname] = ii
            dct[r].children.append(ii)
    print(f'### tstat = {tstat:.3f} tcls = {tcls:.3f}')
    return root

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

def process2(root):
    # load into object relational mapping
    t0 = time()
    root = process(root)
    #dfs
    t1 = time()
    # fictitious root lets you use the "subtree depths" to group any variable by depth
    fictitious_root = Directory(None, None, root.st)
    fictitious_root.add_child(root) 
    accs1, P = dfs(fictitious_root)
    for k in 'ndir', 'nsym', 'nrf', 'nchild':
        accs1[k].pop(0)
    # lca
    t2 = time()
    accs2 = least_common_ancestor(root, P)
    # analytics
    t3 = time()
    print('link type', 'count')
    for k in accs2:
        print(k, accs2[k])
    print('target type', 'count')
    for k, v in pointerdist(P).items():
        print(k, v)

    for k in "depths", "hlinks", "nchild", "nrf":
        m, s = mean_std(accs1[k])
        print(f'mean {k} = {m:.2f}')
        print(f'std {k} =  {s:.2f}')

    import pandas as pd
    df = pd.DataFrame({'level': accs1['subtree_depths'],
                       'subtree_size': accs1['subtree_sizes'],
                       'subtree_depth': accs1['subtree_nested_depths'],
                       'ndir':accs1['ndir'],
                       'nsym':accs1['nsym'],
                       'nrf':accs1['nrf'],
                       'nchild':accs1['nchild']})
    #
    print('mean depth by directory', 
          f"{df['level'].mean():.2f}",
          'std',
          f"{df['level'].std():.2f}")
    #
    gr = df.groupby('level').agg(['mean','std'])
    std_o_mean = gr[('subtree_size', 'std')] / gr[('subtree_size','mean')]
    gr[('subtree_size', 'std/mean')] = std_o_mean
    print('mean, std, std/mean of subtree size grouped by level (gives branch number/branch factor, including files as branches)')
    print(gr.round(2))
    print('mean(std/mean) for branch factor is', f"{std_o_mean.mean():.2f}")
    t4 = time()
    #
    print('times')
    print(f'process={t1-t0:.3f}\n' +
          f'dfs={t2-t1:.3f}\n' +
          f'lca={t3-t2:.3f}\n' + 
          f'analytics={t4-t3:.3f}')

if __name__ == '__main__':
    rootstrs = ('./example', '/etc', '/usr', '/lib')
    process2(rootstrs[3])
