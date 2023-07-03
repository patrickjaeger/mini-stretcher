""""How to queue stuff
source: https://www.youtube.com/watch?v=x1ndXuw7S0s

1. async functions don't run themselves; you need to run them using 
   run_until_complete(func_async)
2. async functions can call other asyncs functions, but yout need to put
   an 'await' in front of the nested async function
"""


from queue import Queue
from threading import Thread
from time import sleep

def producer(q, n):
    for i in range(n):
        q.put(i)
    q.put(None)

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print("Got:", item)

q = Queue()
Thread(target=producer, args=(q, 10)).start()

Thread(target=consumer, args=(q,)).start()

