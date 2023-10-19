from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
import os
# Connect to client
client = ModbusClient(method='rtu', port='COM5',
                      timeout=1, baudrate=9600)


#client.write_register(61, 20, unit=1)



# Ask for current modbus ID number (pretty redundant as we have to know the number)
response = client.read_holding_registers(361, 2, unit=20)

# client.write_registers(0x20, [0x0,0x0], unit=0x01)
# client.write_registers(0x22, [0x0,0x0], unit=0x01)
decoder = BinaryPayloadDecoder.fromRegisters(
    response.registers, Endian.Big, wordorder=Endian.Big)
print(decoder.decode_32bit_float())


response = client.read_holding_registers(363, 2, unit=1)

decoder = BinaryPayloadDecoder.fromRegisters(
    response.registers, Endian.Big, wordorder=Endian.Big)
print(decoder.decode_32bit_int())

response = client.read_holding_registers(61, 1, unit=1)
print(response.registers[0])

input()
# Ask for current modbus ID number (pretty redundant as we have to know the number)

while 1:
    # This requests the temperature
    response = client.read_holding_registers(0x0018, 1, unit=1)
    print(response.registers[0])

    # This requests the current flow rate
    response = client.read_holding_registers(0x0020, 2, unit=1)
    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, Endian.Big, wordorder=Endian.Little)
    print(decoder.decode_32bit_int())

    # This requests the cumulative flow
    response = client.read_holding_registers(0x0022, 2, unit=1)
    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, Endian.Big, wordorder=Endian.Little)
    print(decoder.decode_32bit_int())

    time.sleep(0.1)
    os.system('cls')
print(response.registers[0])

#client.write_registers(0x3100, [0x0], unit=0x01)


input()


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
