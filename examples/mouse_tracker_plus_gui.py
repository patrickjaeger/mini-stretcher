from pynput.mouse import Listener
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

counter = 0

def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))

def on_click(x, y, button, pressed):
    global counter
    if  not pressed:
        counter += 1
        print(f"counter: {counter}")
    if counter == 3:
        counter = 0
        print("tracker stopped")
        return False
        
def on_scroll(x, y, dx, dy):
    print('Scrolled {0}'.format((x, y)))

def create_listener():
    l1 = Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) 
    l1.start()

def test_print():
    print("banana")

class TestFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=(5,5))

        self.b1 = ttk.Button(self, text="Start tracker", command=create_listener)
        self.b1.pack(side="left", padx=10)
        
        self.b2 = ttk.Button(self, text="banana", command=test_print)
        self.b2.pack(side="right", padx=10)


if __name__ == "__main__":
    app = ttk.Window("test", "darkly")
    TestFrame(app).pack()
    app.mainloop()
