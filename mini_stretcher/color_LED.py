import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ColorLED(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.diameter = 15
        
        self.led = ttk.Canvas(self, height=self.diameter, width=self.diameter)
        self.led.pack()
        self.set_color()

    def set_color(self, color="red"): 
        self.led.create_oval(0, 0, self.diameter, self.diameter, fill=color)