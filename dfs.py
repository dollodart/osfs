from env import DEVNULL
from thisfiles import *
from thisstats import mean

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
