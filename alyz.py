from thisfiles import *
from thisstats import mean, mean_std, pointerdist
from thisio import load_app_memory
from dfs import dfs
from lca import least_common_ancestor
from time import time

def alyz_fs(root_str):
    # load into object relational mapping
    t0 = time()
    root = load_app_memory(root_str)
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
    alyz_fs(rootstrs[1])
