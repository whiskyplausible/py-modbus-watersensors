import logging
import serial
import serial.tools.list_ports

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# Connect to client
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
    print(port, desc, hwid)
    if "067B:2303" in hwid: # detect where teensy is plugged in 
        client_port = port



client = ModbusClient(method='rtu', port=client_port,
                      timeout=1, baudrate=9600)

# # This writes a new unit ID to the sensor. The unit id is the 1 in the [0x010] so unit 2 would be [0x020]
# original_unit = 5120  # 0x1

# new_unit = 0x01
# command = hex(new_unit) + "00"
# print()
# print(int(command, 0))

# #client.write_registers(0x3000, [0x0100], unit=0x0E)
# client.write_registers(0x3000, [int(command, 0)], unit=original_unit)

# # This requests the current unit number of the device
# response = client.read_holding_registers(0x3000, 1, unit=0xFF)
# print("address ", response.registers)


# This works to read sensors readings from the unit from factory
response = client.read_holding_registers(0x2000, 6, unit=0x14)
print(response.registers)

# Read the temperature (in first two registers)
decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
print(decoder.decode_32bit_float())

# Read tubidity (3rd and 4th registers)
decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
print(decoder.decode_32bit_float())

# Read tubidity (3rd and 4th registers)
decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[4], response.registers[5]], Endian.Little, wordorder=Endian.Little)
print(decoder.decode_32bit_float())


# Just a test one from the documentation this should yield a temperature of 17.625.
decoder = BinaryPayloadDecoder.fromRegisters(
    [0000, 0x8d41], Endian.Little, wordorder=Endian.Little)
print("test!", decoder.decode_32bit_float())

# Now trying to split individual readings up to help reading them on the Arduino code

response = client.read_holding_registers(0x2100, 2, unit=0x14)
decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
print("***************", decoder.decode_32bit_float())
