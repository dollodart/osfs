import pandas as pd
import matplotlib.pyplot as plt
from time import time
from datetime import datetime
from stat import *
from thisfiles import *

class StatResult:
    def __init__(self, st_mode=0,
            st_ino=0,
            pst_ino=0,
            st_nlink=0,
            st_uid=0,
            st_gi=0, 
            st_rdev=0, 
            st_size=0, 
            st_blksize=0, 
            st_blocks=0, 
            st_atime=0, 
            st_mtime=0, 
            st_ctime=0):
        self.st_mode = st_mode
        self.st_ino = st_ino
        self.pst_ino = pst_ino
        self.st_nlink = st_nlink
        self.st_uid = st_uid
        self.st_gi = st_gi 
        self.st_rdev = st_rdev
        self.st_size = st_size
        self.st_blksize = st_blksize
        self.st_blocks = st_blocks
        self.st_atime = st_atime
        self.st_mtime = st_mtime
        self.st_ctime = st_ctime


def gen_nodes():
    lim = 10000
    t0 = time()
    root = Directory(None, '', StatResult())
    with open('filesystem', 'r') as _:
        # fpath,level,st_mode,st_nlink,st_uid,st_gi,st_rdev,st_size,st_blksize,st_blocks,st_atime,st_mtime,st_ctime,
        for i, line in enumerate(_.readlines()[1:]): # skip header column
            fpath, *metadata = line.split(',')
            try:
                level, st_mode, st_ino,\
                pst_ino, st_nlink, st_uid,\
                st_gi, st_rdev, st_size,\
                st_blksize, st_blocks, st_atime,\
                st_mtim, st_ctime, _ = metadata
            except ValueError:
                continue

            lstat = StatResult(
                    int(st_mode),
                    int(st_ino),
                    int(pst_ino),
                    int(st_nlink),
                    int(st_uid),
                    int(st_gi),
                    int(st_rdev),
                    int(st_size),
                    int(st_blksize),
                    int(st_blocks),
                    int(st_atime),
                    int(st_mtim),
                    int(st_ctime))

            fpath = fpath.split('/')
            name = fpath[-1]
            parent = '/'.join(fpath[:-1])
            try:
                parent = File.total_dir[parent]
            except KeyError:
                print('parent not found before child in depth first search, impossible')
                continue
            try:
                cls = factorydct[S_IFMT(lstat.st_mode)]
            except KeyError:
                print('error in st_mode of lstat object', lstat.st_mode)
                continue
            n = cls( parent, name, lstat)

            if parent.__class__ == Directory:
                parent.add_child(n)

            if i > lim:
                print('at', i, 'time', time() - t0)
                lim += 10000
    return root

if __name__ == '__main__':
    root = gen_nodes()
    from dfs import dfs
    a, P = dfs(root)
    print(a)
