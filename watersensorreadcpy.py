from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import logging
# Connect to client
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = ModbusClient(method='rtu', port='/dev/ttyUSB0',
                      timeout=1, baudrate=9600)

# Ask for current modbus ID number (pretty redundant as we have to know the number)
response = client.read_holding_registers(0x2600, 5, unit=1)
print(response.registers)

decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
print(decoder.decode_32bit_float())

decoder = BinaryPayloadDecoder.fromRegisters(
    [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
print(decoder.decode_32bit_float())

decoder = BinaryPayloadDecoder.fromRegisters(
    [0000, 0x8d41], Endian.Little, wordorder=Endian.Little)
print("test!", decoder.decode_32bit_float())


r = input()
# Ask for measurement value
response = client.read_holding_registers(0x01, 2, unit=1)
decoder = BinaryPayloadDecoder.fromRegisters(
    response.registers, Endian.Big, wordorder=Endian.Little)
print(decoder.decode_32bit_float())


# Ask unit for current temperature (I think this register is temp in all the units)
# Temp saved as 2 x 16bit values, so we read two, then use pymodbus decoder stuff
# to get a float value out of this.
response = client.read_holding_registers(0x03, 2, unit=1)
decoder = BinaryPayloadDecoder.fromRegisters(
    response.registers, Endian.Big, wordorder=Endian.Little)
print(decoder.decode_32bit_float())


# The current modbus ID to 1.
#client.write_register(0x19, 1, unit=2)
