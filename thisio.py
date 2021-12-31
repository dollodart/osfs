import os
from time import time
from thisfiles import *

import threading
from queue import Queue

class PathThread(threading.Thread):
    accumulator = dict()

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def printfiles(self, p):
        for r, s, f in os.walk(p, topdown=True):
            for i in s + f:
                fname = os.path.join(r, i)
                try:
                    st = os.lstat(fname)
                    cls = factorydct[S_IFMT(st.st_mode)]
                except FileNotFoundError: # file doesn't exist or can't be accessed
                    continue
                except KeyError: # unsupported filetype
                    continue
                ii = cls(self.__class__.accumulator[r], i, st)
                self.__class__.accumulator[fname] = ii
                self.__class__.accumulator[r].children.append(ii)

    def run(self):
        while True:
            path = self.queue.get()
            self.printfiles(path)
            self.queue.task_done()

def load_app_memory_parallel(paths, nthread=2):

    roots = []
    for str_root in paths:
        root = Directory(None, str_root, os.lstat(str_root))
        PathThread.accumulator[root.name] = root
        roots.append(root)

    # threadsafe queue
    pathqueue = Queue()

    # spawn threads
    for i in range(nthread):
        t = PathThread(pathqueue)
        t.setDaemon(True)
        t.start()

    # add paths to queue
    for path in paths:
        pathqueue.put(path)

    # wait for queue to get empty
    pathqueue.join()

    return roots

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
