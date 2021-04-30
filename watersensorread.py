from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

# Connect to client
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout=1, baudrate=9600)

# Ask for current modbus ID number (pretty redundant as we have to know the number)
response = client.read_holding_registers(0x19,1, unit=1)
print(response.registers)

# Ask unit for current temperature (I think this register is temp in all the units)
# Temp saved as 2 x 16bit values, so we read two, then use pymodbus decoder stuff
# to get a float value out of this.
response = client.read_holding_registers(0x03,2, unit=1)
decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
print(decoder.decode_32bit_float())


# The current modbus ID to 1.
client.write_register(0x19, 1, unit=2)
