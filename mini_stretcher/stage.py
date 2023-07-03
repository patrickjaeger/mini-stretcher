from zaber_motion import Library, Units
from zaber_motion.binary import *
from pynput.mouse import Listener
from time import sleep

Library.enable_device_db_store()

class Protocol():
    DEFAULT_SPEED = 5  # [mm/s]
    ZERO_POSITION = 497639  # [data]; max. motor position: 533334 
    CHAMBER_LENGTH = 12.5  # hole center to hole center [mm]
    DEFAULT_STRAIN = 50  # [%]
    DEFAULT_STRAIN_RATE = 0.5  # [%/s]

def start(port = "COM3") -> None:
    """Open connection to motors"""
    global con1
    con1 = Connection.open_serial_port(port)
    global d1, d2
    d1, d2 = con1.detect_devices()
    print(con1)
    print(d1)
    print(d1)

def finish() -> None:
    """"Close motor connection"""
    con1.close()
    print("CONNECTION CLOSED")

def home() -> None:
    """Home both stages"""
    con1.generic_command(0, CommandCode.HOME, timeout=5)

def zero() -> None:
    """Move both stages the zero position"""
    d1.settings.set(BinarySettings.TARGET_SPEED, 
                    Protocol.DEFAULT_SPEED, 
                    Units.VELOCITY_MILLIMETRES_PER_SECOND)
    d2.settings.set(BinarySettings.TARGET_SPEED, 
                    Protocol.DEFAULT_SPEED, 
                    Units.VELOCITY_MILLIMETRES_PER_SECOND)
    
    d1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, 
                                   Protocol.ZERO_POSITION)
    d2.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, 
                                   Protocol.ZERO_POSITION)
    
    print("POSITION: zero")

def mm_to_data(length_mm: float) -> int:
    """Convert millimeters to zaber data units
    default microstep size: 0.047625 µm
    position = data[micron] * (Microstep Size[micron]) 
    """
    return round(length_mm * 1000 / 0.047625)

# def mms_to_data(speed_mms: float) -> int:
#     """Convert millimeters per second to zaber data units
#     default microstep size: 0.047625 µm
#     velocity = data * (Microstep Size) / (1.6384 s) 
#     """
#     return round(speed_mms * 1000 / 0.047625 * 1.6384)

def stretch(strain: float, strain_rate: float, pause: float) -> None:
    """Stretch chamber

    Args:
        strain (float): target strain [%]
        strain_rate (float): strain rate [%/s]
        pause (float): time to pause before stretch [s]
    """

    chamber_end_length = Protocol.CHAMBER_LENGTH * (1 + strain / 100)
    delta_x = (chamber_end_length - Protocol.CHAMBER_LENGTH) / 2
    position = Protocol.ZERO_POSITION - mm_to_data(delta_x)
    
    speed = strain_rate / 100 * Protocol.CHAMBER_LENGTH

    # Set speed
    d1.settings.set(BinarySettings.TARGET_SPEED, 
                    speed/2, 
                    Units.VELOCITY_MILLIMETRES_PER_SECOND)
    d2.settings.set(BinarySettings.TARGET_SPEED, 
                    speed/2, 
                    Units.VELOCITY_MILLIMETRES_PER_SECOND)

    for s in range(pause):
        countdown = pause - s
        print("Start in: ", countdown)
        sleep(1)

    # Send move commands
    d1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position)
    d2.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position)
    
    print("POSITION: max. strain")

def stop() -> None:
    """Stops both motors"""
    d1.stop()
    d2.stop()
    
def current_position():
    """Check current motor positions"""
    pos = [d1.settings.get(BinarySettings.CURRENT_POSITION), 
           d2.settings.get(BinarySettings.CURRENT_POSITION)]
    print(pos)
    print(f"Position equal: {pos[0] == pos[1]}")
    

# Trigger

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

    
