import os

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from zaber_motion import Units, Library
from zaber_motion.binary import Connection, BinarySettings, CommandCode
from mini_stretcher import color_LED
from pynput.mouse import Listener
from time import sleep


Library.enable_device_db_store(os.path.dirname(__file__) + "/zaber_device_db")


class Motors:
    ZERO_POSITION = 503937

    def __init__(self):
        self.connected = False

    def connect(self, port):
        self.connection = Connection.open_serial_port(port)
        try:
            self.device1 = self.connection.detect_devices()[0]
            self.device2 = self.connection.detect_devices()[1]
            self.connected = True
        except Exception as e:
            self.connection.close()
            raise e

    def disconnect(self):
        self.connected = False
        self.connection.close()

    def stop(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.device1.stop()
        self.device2.stop()

    def home(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.device1.generic_command_no_response(CommandCode.HOME)
        self.device2.generic_command_no_response(CommandCode.HOME)

    def move_relative_distance(self, length, speed):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.device1.settings.set(BinarySettings.TARGET_SPEED, speed / 2, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.device2.settings.set(BinarySettings.TARGET_SPEED, speed / 2, Units.VELOCITY_MILLIMETRES_PER_SECOND)

        self.device1.generic_command_no_response(CommandCode.MOVE_RELATIVE, self.mm_to_data(-length / 2))
        self.device2.generic_command_no_response(CommandCode.MOVE_RELATIVE, self.mm_to_data(-length / 2))

    def move_absolute_distance(self, pos, speed):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.device1.settings.set(BinarySettings.TARGET_SPEED, speed / 2, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.device2.settings.set(BinarySettings.TARGET_SPEED, speed / 2, Units.VELOCITY_MILLIMETRES_PER_SECOND)

        position = self.ZERO_POSITION - self.mm_to_data((pos - 12) / 2)
        self.device1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position)
        self.device2.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position)

    def get_positions(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        return self.device1.settings.get(BinarySettings.CURRENT_POSITION), self.device2.settings.get(BinarySettings.CURRENT_POSITION)

    def mm_to_data(self, length_mm: float) -> int:
        """Convert millimeters to zaber data units
        default microstep size: 0.047625 µm
        position = data[micron] * (Microstep Size[micron])
        """
        return round(length_mm * 1000 / 0.047625)


class Protocol:
    L0 = None
    TARGET_LENGTH = None
    PAUSE = None
    SPEED = None


class SetupFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motors):
        super().__init__(master, text="Setup", padding=(5, 5))

        self.port_var = ttk.StringVar(value="COM3")
        self.port_ent = ttk.Entry(self, textvariable=self.port_var, width=6)
        # self.port_ent.configure(validate="key", validatecommand=(self.register(self.validator), "%P",))
        self.port_ent.grid(row=0, column=0, padx=5, pady=2)

        self.connect_btn = ttk.Button(self, text="Connect", command=self.on_connect_click)
        self.connect_btn.grid(row=0, column=1, padx=5, pady=2, sticky=EW)

        self.connect_led = color_LED.ColorLED(self)
        self.connect_led.grid(row=0, column=2, padx=5, pady=2)

        self.home_btn = ttk.Button(self, text="Home stages", state="disabled", command=self.on_home_click)
        self.home_btn.grid(row=1, column=1, padx=5, pady=2)

        self.home_led = color_LED.ColorLED(self)
        self.home_led.grid(row=1, column=2, padx=5, pady=2)

        self.connection_state = "naive"
        self.connection = None
        self.home_state = "naive"
        self.device1 = None
        self.device2 = None

        self.motors = motors

    # def validator(self, P):
    #     return P.isdigit() or P == ""

    # def validator(self, P):
    # return P.__len__() or P == ""

    def on_connect_click(self):
        if self.connection_state == "naive":
            try:
                self.motors.connect(self.port_var.get())
            except Exception as e:
                print(e)
            else:
                self.connection_state = "connected"
                self.connect_btn.configure(bootstyle="danger", text="Disconnect")
                self.connect_led.set_color("green")
                self.home_btn.configure(state="enabled")
        elif self.connection_state == "connected":
            try:
                self.motors.disconnect()
            except:
                return
            else:
                self.connection_state = "naive"
                self.connect_btn.configure(bootstyle="defaul", text="Connect")
                self.connect_led.set_color("red")
                self.home_led.set_color("red")

    def on_home_click(self):
        try:
            self.motors.home()
            self.home_led.set_color("yellow")
        except Exception as e:
            print(e)
        else:
            self.home_btn.configure(state="disabled")
            self.home_state = "homed"
            self.home_led.set_color("green")

    def callback(self):
        print(self.port_var.get())


class ManualMove(ttk.Labelframe):
    def __init__(self, master, motors: Motors):
        super().__init__(master, text="Manual move", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1, minsize=120)
        self.columnconfigure(1, weight=1)

        self.length_var = ttk.StringVar()
        self.length_var.set("12")
        self.speed_var = ttk.StringVar()
        self.speed_var.set("2")

        self.length_lbl = ttk.Label(self, text="Length [mm]")
        self.length_lbl.grid(row=0, column=0, sticky=E)
        self.length_ent = ttk.Entry(self, textvariable=self.length_var, width=6, justify="right")
        self.length_ent.grid(row=0, column=1, padx=5, pady=2, sticky=EW)

        self.speed_lbl = ttk.Label(self, text="Speed [mm/s]")
        self.speed_lbl.grid(row=1, column=0, sticky=E)
        self.speed_ent = ttk.Entry(self, textvariable=self.speed_var, width=6, justify="right")
        self.speed_ent.grid(row=1, column=1, padx=5, pady=2, sticky=EW)

        self.move_btn = ttk.Button(self, text="Move", command=self.on_move_click)
        self.move_btn.grid(row=3, column=1, padx=5, pady=5, sticky=EW)

        self.motors = motors

    def on_move_click(self):
        try:
            self.motors.move_absolute_distance(float(self.length_var.get()), float(self.speed_var.get()))
        except Exception as e:
            print(e)


class ProtocolFrame(ttk.Labelframe):
    def __init__(self, master: Motors, protocol: Protocol):
        super().__init__(master, text="Protocol", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1, minsize=120)
        self.columnconfigure(1, weight=1)

        self.len_zero_var = ttk.StringVar()
        self.len_zero_var.set("12")
        self.len_target_var = ttk.StringVar()
        self.len_target_var.set("14")
        self.pause_var = ttk.StringVar()
        self.pause_var.set("10")
        self.speed_var = ttk.StringVar()
        self.speed_var.set("0.03")

        self.len_zero_lab = ttk.Label(self, text="L0 [mm]")
        self.len_zero_lab.grid(row=0, column=0, sticky=E)
        self.len_zero_ent = ttk.Entry(self, textvariable=self.len_zero_var, width=6, justify="right")
        self.len_zero_ent.grid(row=0, column=1, padx=5, pady=2, sticky=E)

        self.len_target_lab = ttk.Label(self, text="Target length [mm]")
        self.len_target_lab.grid(row=1, column=0, sticky=E)
        self.len_target_ent = ttk.Entry(self, textvariable=self.len_target_var, width=6, justify="right")
        self.len_target_ent.grid(row=1, column=1, padx=5, pady=2, sticky=E)

        self.pause_lab = ttk.Label(self, text="Pause [s]")
        self.pause_lab.grid(row=2, column=0, sticky=E)
        self.pause_ent = ttk.Entry(self, textvariable=self.pause_var, width=6, justify="right")
        self.pause_ent.grid(row=2, column=1, padx=5, pady=2, sticky=E)

        self.speed_lab = ttk.Label(self, text="Speed [mm/s]")
        self.speed_lab.grid(row=3, column=0, sticky=E)
        self.speed_ent = ttk.Entry(self, textvariable=self.speed_var, width=6, justify="right")
        self.speed_ent.grid(row=3, column=1, padx=5, pady=2, sticky=E)

        protocol.L0 = self.len_zero_var
        protocol.TARGET_LENGTH = self.len_target_var
        protocol.PAUSE = self.pause_var
        protocol.SPEED = self.speed_var


class ControlsFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motors, protocol: Protocol):
        super().__init__(master, text="Controls", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.run_btn = ttk.Button(self, text="Run protocol", bootstyle="secondary", command=self.on_run_click)
        self.run_btn.grid(row=0, column=0, padx=5, pady=5, sticky=EW)

        self.goto_zero_btn = ttk.Button(self, text="Go to L0", bootstyle="default", command=self.on_goto_zero_click)
        self.goto_zero_btn.grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        self.trigger_btn = ttk.Button(self, text="Arm trigger", bootstyle="warning", command=self.on_trigger_click)
        self.trigger_btn.grid(row=1, column=0, padx=5, pady=5, sticky=EW)

        self.stop_btn = ttk.Button(self, text="STOP", bootstyle="danger", command=self.on_stop_click)
        self.stop_btn.grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        self.motors = motors
        self.protocol = protocol

    def on_goto_zero_click(self):
        try:
            self.motors.move_absolute_distance(float(self.protocol.L0.get()), 5)
        except Exception as e:
            print(e)

    def on_run_click(self):
        try:
            pause = int(self.protocol.PAUSE.get())
            for i in range(pause):
                print(f"START in {pause - i} seconds")
                sleep(1)
            self.motors.move_absolute_distance(float(self.protocol.TARGET_LENGTH.get()), float(self.protocol.SPEED.get()))
        except Exception as e:
            print(e)

    def on_stop_click(self):
        try:
            self.motors.stop()
        except Exception as e:
            print(e)

    def on_trigger_click(self):
        self.left_counter = 0
        self.right_counter = 0
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()

    def on_click(self, x, y, button, pressed):
        if button._name_ == "left" and not pressed:
            self.left_counter += 1
            print(f"left_counter: {self.left_counter}")

        if button._name_ == "right" and not pressed:
            self.right_counter += 1
            print(f"right_counter: {self.right_counter}")

        if self.left_counter == 3:
            try:
                self.on_run_click()
                print("Protocol LIVE")
            except Exception as e:
                print(e)
            return False

        if self.right_counter == 3:
            print("Trigger stopped")
            return False


class StatusFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motors):
        super().__init__(master, text="Status", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.status_lbl = ttk.Label(self, text="Status:")
        self.status_lbl.grid(row=0, column=0, padx=5, pady=2, sticky=E)
        self.status_out = ttk.Label(self, text="idle")
        self.status_out.grid(row=0, column=1, padx=5, pady=2, sticky=W)

        self.clen_lbl = ttk.Label(self, text="Current length [mm]:")
        self.clen_lbl.grid(row=1, column=0, padx=5, pady=2, sticky=E)
        self.clen_out = ttk.Label(self, text="-")
        self.clen_out.grid(row=1, column=1, padx=5, pady=2, sticky=W)

        self.motors = motors

        self.last_distance = 12
        self.display_values()

    def display_values(self):
        if self.motors.connected:
            pos1, pos2 = self.motors.get_positions()
            distance = ((motors.ZERO_POSITION - pos1) + (motors.ZERO_POSITION - pos2)) / 1000 * 0.047625 + 12
            self.clen_out["text"] = "{:10.4f}".format(distance)
            if self.last_distance != distance:
                self.status_out["text"] = "running"
            else:
                self.status_out["text"] = "idle"
            self.last_distance = distance
        self.after(100, self.display_values)


if __name__ == "__main__":
    # Library.enable_device_db_store()

    app = ttk.Window("miniStretcher", "darkly", resizable=(False, False), iconphoto="icons/banana2.png")

    motors = Motors()
    protocol = Protocol()

    SetupFrame(app, motors).grid(row=0, column=0, sticky=NSEW, padx=5, pady=2)
    ManualMove(app, motors).grid(row=0, column=1, sticky=NSEW, padx=5, pady=2)
    ProtocolFrame(app, protocol).grid(row=1, column=0, rowspan=2, sticky=NSEW, padx=5, pady=2)
    ControlsFrame(app, motors, protocol).grid(row=1, column=1, sticky=NSEW, padx=5, pady=2)
    StatusFrame(app, motors).grid(row=2, column=1, sticky=NSEW, padx=5, pady=2)

    app.mainloop()
