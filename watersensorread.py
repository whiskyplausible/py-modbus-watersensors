from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# Connect to client
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout=1, baudrate=9600)

# Ask for current modbus ID number (pretty redundant as we have to know the number)
response = client.read_holding_registers(0x19,1, unit=2)
print(response.registers)

# The current modbus ID to 1.
client.write_register(0x19, 1, unit=2)
