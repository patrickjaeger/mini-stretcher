from zaber_motion import Library, Units
from zaber_motion.binary import *


Library.enable_device_db_store()

con1 = Connection.open_serial_port("COM3")

devices = con1.detect_devices()
d1 = devices[0]

d1.home()

d1.settings.get(BinarySettings.TARGET_SPEED, Units.VELOCITY_MILLIMETRES_PER_SECOND)
d1.settings.set(BinarySettings.TARGET_SPEED, 0.2, Units.VELOCITY_MILLIMETRES_PER_SECOND)

d1.settings.get(BinarySettings.MAXIMUM_POSITION)
d1.settings.get(BinarySettings.CURRENT_POSITION)

# This is blocking
d1.move_absolute(2, Units.LENGTH_MILLIMETRES)
d1.generic_command_with_units(CommandCode.SET_TARGET_SPEED,)

# This is not
d1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, 500000)

d1.is_busy()
d1.stop()



con1.close()