import os
from time import time
from thisfiles import *

def load_app_memory(string_directory):
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
