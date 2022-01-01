from thisio import load_app_memory, load_app_memory_thread, load_app_memory_multiprocess
from time import time

def test_load_app_memory_serial(dirs):
    t0 = time()
    load_app_memory(dirs[0])
    print('serial', round(time() - t0, 3))

def test_load_app_memory_thread(dirs):
    for nthread in 1, 2, 4, 8, 16:
        t0 = time()
        r = load_app_memory_thread(dirs, nthread)
        print(nthread, round(time() - t0, 3))

def test_load_app_memory_multiprocess(dirs):
    for npool in 1, 2, 4, 8, 16:
        t0 = time()
        r = load_app_memory_multiprocess(dirs[0], npool)
        print(npool, round(time() - t0, 3))

if __name__ == '__main__':
    dirs = ['/usr']
    test_load_app_memory_multiprocess(dirs)