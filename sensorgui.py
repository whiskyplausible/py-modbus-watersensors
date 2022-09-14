
import PySimpleGUI as sg
import pymodbus
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import json
client = ModbusClient(method='rtu', port='/dev/ttyUSB0',
                      timeout=1, baudrate=9600)
settings = {
    "refresh_rate": 500,
    "current_monitor": None
}


def turbidity_update_unit_id(new_id):
    command = hex(new_id) + "00"
    client.write_registers(0x3000, [int(command, 0)], unit=0x0E)


def read_turbidity1():
    readings = {}
    # This works to read from the unit from factory
    try:
        response = client.read_holding_registers(0x2600, 5, unit=1)
    except pymodbus.exceptions.ConnectionException:
        return ["Comms error"]

    # Read the temperature (in first two registers)
    decoder = BinaryPayloadDecoder.fromRegisters(
        [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
    readings["temp"] = decoder.decode_32bit_float()

    # Read tubidity (3rd and 4th registers)
    decoder = BinaryPayloadDecoder.fromRegisters(
        [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
    readings["turbidity"] = decoder.decode_32bit_float()
    return readings


def read_do1():
    return ["not implemented"]


def read_ec1():
    return ["not implemented"]


def read_nitrate1():
    return ["not implemented"]


sensors = {"Turbidity sensor 1": read_turbidity1,
           "DO sensor 1": read_do1,
           "EC sensor 1": read_ec1,
           "Nitrate sensor 1": read_nitrate1
           }

title_font = ("Arial", 20)
reading_font = ("Arial", 15)


layout = [[sg.Text('*'*50)]]


for key in sensors:

    layout.append([sg.Text(key, font=title_font)])
    layout.append(
        [sg.Text("Value 1   \nValue 2                         ", key="sensor__"+key, font=reading_font)])
    layout.append([sg.Button('Monitor', key=key+"__button")])

layout.append([sg.Text('Update freq (ms)', size=(18, 1)),
              sg.InputText(key="update_freq", default_text=settings["refresh_rate"])])
layout.append(
    [sg.Text('What you print will display below:                                       ', key="current_monitor_text")])
layout.append([sg.Output(size=(80, 40), key='-OUTPUT-')]
              )
layout.append([sg.Button('Update'), sg.Button('Cancel')])

window = sg.Window('Sensor readings', layout,
                   element_justification='c', finalize=True)
window['update_freq'].bind("<Return>", "_Enter")


layout2 = [[sg.Text('What you print will display below:', key="current_monitor_text")],
           [sg.Output(size=(50, 10), key='-OUTPUT-')],
           [sg.In(key='-IN-')],
           [sg.Button('Go'), sg.Button('Clear'), sg.Button('Exit')]]

window2 = sg.Window('Window Title', layout2)

while True:
    event, values = window.read(timeout=500)
    # print(event, values)

    for key in sensors:
        window['sensor__'+key].update(
            json.dumps(sensors[key]()))
        if settings["current_monitor"] == key:
            print(json.dumps(sensors[key]()))
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    # print(event)

    if "__button" in event:
        settings["current_monitor"] = event[:-8]
        window["current_monitor_text"].update(
            "Currently monitoring " + event[:-8])

    if "update_freq_Enter" in event:
        if values['update_freq'].isnumeric():
            settings["refresh_rate"] = values['update_freq']
        else:
            window['update_freq'].update(settings["refresh_rate"])
window.close()
