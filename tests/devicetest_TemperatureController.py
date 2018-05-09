from chemiosbrain.temperature_controller import TemperatureController as T
import sys

if len(sys.argv) != 2:
    raise ValueError("Please pass in the serial port")


port = sys.argv[1]
print(port)
omega = T(port,1)

#Set the temperature
temp = omega.get_current_temperature()
print(temp)