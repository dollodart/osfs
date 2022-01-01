import os
from time import time
from thisfiles import *

import threading
from queue import Queue

from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as JQueue

class PathThread(threading.Thread):

    def __init__(self, paths, accumulator=dict()):
        threading.Thread.__init__(self)
        self.paths = paths
        self.accumulator = accumulator

    def process_paths(self, p):
        print('walking at', p)
        for r, s, f in os.walk(p, topdown=True):
            print(r, s, f)
            for i in s + f:
                #print(fname)
                fname = os.path.join(r, i)
                try:
                    st = os.lstat(fname)
                    cls = factorydct[S_IFMT(st.st_mode)]
                except FileNotFoundError: # file doesn't exist or can't be accessed
                    continue
                except KeyError: # unsupported filetype
                    continue
                ii = cls(self.accumulator[r], i, st)
                self.accumulator[fname] = ii
                self.accumulator[r].children.append(ii)

    def run(self):
        while self.paths:
            path = self.paths.pop()
            print('path is', path, 'remaining paths are', self.paths)
            self.process_paths(path)
            print('remaining paths are again', self.paths)
        #self.task_done()

def load_app_memory_multiprocess(root_str, npool=2):
    dct = dict()
    root = Directory(None, root_str, os.lstat(root_str))
    dct[root.name] = root

    unsearched = JQueue()
    for r, s, f in os.walk(root_str): # use listdir, recursively?
        for i in s + f:
            print('pushing', r, i, 'into queue')
            unsearched.put((r, i))

    print('got to joinable queue')

    def class_converter():
        while True:
            r, i = unsearched.get() 
            fname = os.path.join(r, i)
            try:
                st = os.lstat(fname)
                cls = factorydct[S_IFMT(st.st_mode)]
            except FileNotFoundError:
                continue
            except KeyError:
                continue

            ii = cls(dct[r], i, st)
            dct[fname] = ii
            dct[r].children.append(ii)

    print('got past class converter')

    with Pool(npool) as pool:
        for i in range(npool):
            pool.apply_async(class_converter)

    print('got past pool apply async')

    unsearched.join()

    print('got past multiprocessing join')

    return root

def load_app_memory_thread(paths, nthread=2):

    first_roots = []

    if len(paths) < nthread * 2:
        print('going down first depth')
        roots = []

        for str_root in paths:
            root = load_app_memory(str_root, depthlimit=2)
            first_roots.append(root)
            for child in root.children:
                if type(child) is Directory:
                    roots.append(child)
        # todo: may need to go down many depths to find the required number for the threads
        # recursively call this function in such cases
        #if len(roots) < nthread * 2:
        #    load_app_memory_thread([str(r) for r in roots], nthread = ...)
    else:
        roots = [Directory(None, p, os.lstat(p)) for p in paths]

    # distribute each independent subdirectory evenly
    # can't know the size of the subtrees before this, so may be uneven
    mult = len(roots) // nthread

    # spawn threads, operating independently
    # note the objects will be linked from the serial in case they were made
    # but those references are never called
    for i in range(nthread):
        pathqueue = [str(r).lstrip('Directory-')
                for r in roots[i*mult:(i+1)*mult]]
        accumulator = {str(r).lstrip('Directory-'):r
                for r in roots[i*mult:(i+1)*mult]}
        t = PathThread(pathqueue, accumulator) # note: don't need threadsafe queues when they are independent, as here
        t.setDaemon(True)
        print(pathqueue, 'starting now') #accumulator, 'starting now')
        t.start()
        # no join is needed because these are independent threads

    if first_roots:
        return first_roots

    return roots

def load_app_memory(string_directory, depthlimit=None):
    # process to natural correspondence binary tree? would need to retain original parent designation
    dct = dict()
    root = Directory(None, string_directory, os.lstat(string_directory))
    dct[root.name] = root
    tstat = tcls = 0
    for r, s, f in os.walk(root.name, topdown=True):
        if depthlimit is not None and len(r.split('/')) > depthlimit:
            break
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
