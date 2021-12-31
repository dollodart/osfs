from thisio import load_app_memory, load_app_memory_parallel
from time import time
dirs = ['/usr']
t0 = time()
load_app_memory(dirs[0])
print('serial', round(time() - t0, 3))

for nthread in 1, 2, 4, 8, 16:
    t0 = time()
    r = load_app_memory_parallel(dirs, nthread)
    print(nthread, round(time() - t0, 3))
