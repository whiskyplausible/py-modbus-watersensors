import serial
import serial.tools.list_ports
try:
    from pymodbus.client.sync import ModbusSerialClient as ModbusClient
except: 
    from pymodbus.client import ModbusSerialClient as ModbusClient

client_port = None

def find_port():
    for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
        print(port, desc, hwid)
        if "067B:2303" in hwid: # detect where rs-485 usb is plugged in
            return port
    return None

client_port = find_port()

print("Connections reminder: black to 12v negative, red to 12v positive, green to RS485 A, white to RS485 B")

if not client_port:
    print("Can't find RS485 USB device - please insert USB and check drivers are working OK")
    print("Press enter to retry connection")
    input()
    client_port = find_port()
    if not client_port:
        print("Still couldn't find USB port - will now exit. Press enter to close.")
        input()
        exit()

client = ModbusClient(method='rtu', port=client_port,
                      timeout=1, baudrate=9600)


print("Connected to USB at "+client_port+". Press enter to query status of Lafoo sensor.")
input()

unit_id = None

try:
    response = client.read_holding_registers(0x005, 1, unit=1)
except:
    print("Couldn't communicate with device at all, please check USB interface, power supply and all connections to sensor.")
    print("Press enter to quit")
    input()
    exit()


try:
    unit_id = response.registers[0]
    print("Found device at id = 1")
except AttributeError:
    print("Couldn't find any device at id = 1")


if not unit_id:
    response = client.read_holding_registers(0x005, 1, unit=55)
    try:
        unit_id = response.registers[0]
        print("Found device at id = 55")
    except AttributeError:
        print("Coulnd't find device at id = 55")
        print("Please check USB interface, power supply and all connections to sensor.")
        print("Press enter to quit")
        input()
        exit()

if unit_id != 55:
    print("Switching sensor id from "+str(unit_id)+" to 55")
    client.write_register(0x005, 55, unit=unit_id)
    unit_id = 55

print("Setting output units to bar")
client.write_register(0x009, 1, unit=55)
print("All done, sensor is ready to use")
print("Press enter to quit")
input()
