"""
Components:
    1. Model
        - connection
        - devices
        - methods to move devices, or return their position (mostly
          already included in Devices class)
    2. View
        - setup
        - led
        - home
        - manual move
        - settings
        - controls
        - status
    3. Controller
        - calls the widgets, e.g. self.setup = Setup()
        - handles config of widget elements, 
          e.g. self.setup.connect_btn.config(command=self.open_connection)
        - updates widgets, e.g. self.on_connection_change(self.setup.connection_status.get())
          with on_connection_change(self, connection_status): self.setup.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from zaber_motion import Units, Library
from zaber_motion.binary import Connection, DeviceSettings, BinarySettings, CommandCode


class MiniStretcherModel:
    def __init__(self, com_port="COM3", min_distance = 12):
        # Hardware
        # Minimal distance with motors in end position
        self.min_distance = min_distance
        # TODO Look up actual device_max value
        self.device_max = 24.3  # [mm] from zaber console
        # Setup
        self.connection_status = "disconnected"
        self.homing_status = "naive"
        # Manual move
        self.manual_move_length = 12  # [mm]
        self.manual_move_speed = 5  # [mm/s]
        # Protocol
        self.l_zero = 12        # [mm]
        self.pause = 10         # [s]
        self.strain = 50        # [%]
        self.strain_rate = 0.5  # [%/s]
        # Zaber
        Library.enable_device_db_store()
        self.com_port = com_port
        self.connection = None
        self.status = "idle"
        self.device1, self.device2 = self.connection.detect_devices()

    def set_com_port(self, com_port):
        self.com_port = com_port

    def open_connection(self):
        self.connection = Connection.open_serial_port(self.com_port)
    
    def close_connection(self):
        self.connection = Connection.close()
    
    def home_stretcher(self):
        self.device1.generic_command_no_response(CommandCode.HOME)
        self.device2.generic_command_no_response(CommandCode.HOME)
        
    def check_homing_status(self):
        d1_status = self.device1.settings.get(BinarySettings.HOME_STATUS)
        d2_status = self.device2.settings.get(BinarySettings.HOME_STATUS)
        # TODO Figure out actual value returned from motors
        if d1_status == "homed" and d2_status == "homed":
            return "homed"
        else:
            return "naive"
    
    def set_manual_move_attr(self, attr, value):
        if attr == "length": self.manual_move_length = value
        if attr == "speed": self.manual_move_speed = value
        
    def convert_mm_to_binary(self, mm):
        # TODO Find actual conversion factor
        return mm * 999 # add ROUND
    
    def manual_move(self):
        # TODO Figure out mm to binary conversion
        # binary_length = self.manual_move_target_length * 
        # self.device1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, )
        pass

    def set_protocol_attr(self, attr, value):
        if attr == "zero_position": self.l_zero = value
        if attr == "pause": self.pause = value
        if attr == "strain": self.strain = value
        if attr == "strain_rate": self.strain_rate = value
        

    def set_speed(self, speed):
        self.device1.settings.set(BinarySettings.TARGET_SPEED, 
                                  speed, 
                                  Units.VELOCITY_MILLIMETRES_PER_SECOND)
        self.device2.settings.set(BinarySettings.TARGET_SPEED, 
                                  speed, 
                                  Units.VELOCITY_MILLIMETRES_PER_SECOND)
    
    def move_to_zero_position(self):
        self.set_speed(self.manual_move_speed)
        position_mm = self.device_max - (self.manual_move_length - self.min_distance)/2
        position_bin = self.convert_mm_to_binary(position_mm)
        self.device1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position_bin)
        self.device2.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position_bin)
    
    def stop(self):
        self.device1.generic_command_no_response(CommandCode.STOP)
        self.device2.generic_command_no_response(CommandCode.STOP)
    
    def run_protocol(self):
        l_end = self.l_zero * (1 + self.strain/100)
        speed_mms = (l_end - self.l_zero)/120
        self.set_speed(speed_mms)
        position_mm = self.device_max - (self.manual_move_length - self.min_distance)/2
        position_bin = self.convert_mm_to_binary(position_mm)
        self.device1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position_bin)
        self.device2.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position_bin)
    
    def arm_trigger(self):
        # TODO Implement this in a separate class
        pass

    def get_status(self):
        return self.status
    
    def get_position(self):
        p1 = self.device1.settings.get(BinarySettings.CURRENT_POSITION, Units.LENGTH_MILLIMETRES)
        p2 = self.device2.settings.get(BinarySettings.CURRENT_POSITION, Units.LENGTH_MILLIMETRES)
        # TODO Do the math: max_position - p1 ...

    



class MiniStretcherView():
    def __init__(self):
        pass
        # self.setup = msf.Frame()
        # self.home = msf.Home()

        
        