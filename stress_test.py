import time
import math
import multiprocessing

def burner():
    while True:
         math.sqrt(64*64*64*64*64)

if __name__ == '__main__':
    print("Starting synthetic CPU spike (4 cores)...")
    procs = []
    for _ in range(4):
        p = multiprocessing.Process(target=burner)
        p.start()
        procs.append(p)
        
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            p.terminate()
