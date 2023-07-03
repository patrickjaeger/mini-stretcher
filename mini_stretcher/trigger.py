from pynput.mouse import Listener
from zaber_stuff import stretch

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
        print("Protocol LIVE")
        stretch(strain=50, strain_rate=0.5, pause=10)
        return False

    if right_counter == 3:
        right_counter = 0
        print("Trigger stopped")
        return False


def trigger():
    listener = Listener(on_click=on_click)
    listener.start()

