from pynput.mouse import Listener

def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))

# def on_click(x, y, button, pressed):
#     print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
#     if not pressed:
#         # Stop listener
#         return False

left_counter = 0
right_counter = 0

def on_click(x, y, button, pressed):
    global left_counter
    global right_counter

    if button._name_ == "left" and not pressed:
        left_counter += 1
        print(f"left_counter: {left_counter}")
    if button._name_ == "right" and not pressed:
        right_counter += 1
        print(f"right_counter: {right_counter}")

    if left_counter == 3:
        left_counter = 0
        print("tracker stopped")
        return False
    if right_counter == 3:
        right_counter = 0
        print("Trigger stopped")
        return False
        

def on_scroll(x, y, dx, dy):
    print('Scrolled {0}'.format((x, y)))

# Collect events until released; the join() makes the listener
# blocking - without join(), the listener runs concurrently
with Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll) as listener:
    listener.join()


"""
In concurrent programming, we may need to wait until another thread has 
finished running. This may be for many reasons, such as:

    - The current thread needs a result from the target thread.
    - A resource is shared between the current and target threads.
    - The current thread has no other work to complete.

The join() method provides a way for one thread to block until another 
thread has finished.

source: https://superfastpython.com/join-a-thread-in-python/
"""


l1 = Listener( on_move=on_move, on_click=on_click, on_scroll=on_scroll) 
l1.start()
l1.is_alive()
l1
l1.join()
l1
del l1

"""
You cannot restart a thread in Python, instead you must create and start 
a new thread with the same configuration.

source: https://superfastpython.com/restart-a-thread-in-python/
"""
