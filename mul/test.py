from multiprocessing import Pool
import time

def f(x):
    print(x*x)

if __name__ == '__main__':
    pool = Pool()
    #pool.map(f, range(10))

    r = pool.map_async(f, range(10))

    r.get()