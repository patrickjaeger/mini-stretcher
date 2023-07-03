# source: https://medium.datadriveninvestor.com/the-most-simple-explanation-of-threads-and-queues-in-python-cbc206025dd1
# .task_done() explanation: https://stackoverflow.com/questions/49637086/python-what-is-queue-task-done-used-for
# collections.deque: if you need a general-purpose queue rather than an inter-thread message channel (queue.Queue)
import queue
import threading
import time

def func(q, thread_no):
    while True:
        task = q.get()  # Gets items from the queue
        time.sleep(2)
        q.task_done()  # Reports if work is done so .join() can close up the shop
        print(f'Thread #{thread_no} is doing task #{task} in the queue.')

q = queue.Queue()

# The threads are started and they all run func(). They continuously
# check whether there are items in the queue and process them if they find
# something.
for i in range(4):
    worker = threading.Thread(target=func, args=(q, i,), daemon=True)
    worker.start()

# Here we just put numbers in the queue
for j in range(10):
    q.put(j)
    
q.join()