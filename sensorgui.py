
import PySimpleGUI as sg
import pymodbus
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import json
import threading
import time
from queue import Queue
import datetime
import serial.tools.list_ports

q = Queue(maxsize=3)
client_port = ""
for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
    print(port, desc, hwid)
    if "067B:2303" in hwid: # detect where teensy is plugged in 
        client_port = port

client = ModbusClient(method='rtu', port=client_port,
                      timeout=1, baudrate=9600)
settings = {
    "refresh_rate": 500,
    "current_monitor": None
}
refresh_rate = settings["refresh_rate"]
log_on = False


def RMD_EC_update_unit_id(new_id):
    client.write_register(0x14, new_id, unit=1)


def read_RMD_EC():
    readings = {}
    # This works to read from the unit from factory
    try:
        response = client.read_holding_registers(0x2600, 5, unit=1)
    except pymodbus.exceptions.ConnectionException:
        return ["Comms error"]

    # # Read the temperature (in first two registers)
    # decoder = BinaryPayloadDecoder.fromRegisters(
    #     [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
    # readings["temp"] = decoder.decode_32bit_float()
    try:
        # # Read EC
        response = client.read_holding_registers(0x00, 2, unit=1)
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers, Endian.Big, wordorder=Endian.Little)
        readings["EC"] = round(decoder.decode_32bit_float(), 2)

        # # Read temperature
        response = client.read_holding_registers(0x04, 2, unit=1)
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers, Endian.Big, wordorder=Endian.Little)
        readings["temp"] = round(decoder.decode_32bit_float(), 2)

    except AttributeError:
        return ["error decoding"]
    return readings


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
    try:
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
        readings["temp"] = decoder.decode_32bit_float()

        # Read tubidity (3rd and 4th registers)
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
        readings["turbidity"] = decoder.decode_32bit_float()
    except AttributeError:
        return ["Error decoding"]

    return readings


def read_remond_DO():
    readings = {}
    # This works to read from the unit from factory
    try:
        response = client.read_holding_registers(0x00, 4, unit=1)
    except pymodbus.exceptions.ConnectionException:
        return ["Comms error"]

    # Read the temperature (in first two registers)
    try:
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
        readings["DO_remond"] = decoder.decode_32bit_float()

        # Read tubidity (3rd and 4th registers)
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
        readings["temp_remond_DO"] = decoder.decode_32bit_float()
    except AttributeError:
        return ["Error decoding"]

    return readings


def read_do1():
    try:
        response = client.read_holding_registers(0x2000, 6, unit=0x14)
    except pymodbus.exceptions.ConnectionException:
        return ["Comms error"]
    # Read the temperature (in first two registers)
    try:
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[0], response.registers[1]], Endian.Little, wordorder=Endian.Little)
        # print(decoder.decode_32bit_float())
        readings["temperature"] = decoder.decode_32bit_float()

        # Read tubidity (3rd and 4th registers)
        decoder = BinaryPayloadDecoder.fromRegisters(
            [response.registers[2], response.registers[3]], Endian.Little, wordorder=Endian.Little)
        readings["DO"] = decoder.decode_32bit_float()

        # # Read tubidity (3rd and 4th registers)
        # decoder = BinaryPayloadDecoder.fromRegisters(
        #    [response.registers[4], response.registers[5]], Endian.Little, wordorder=Endian.Little)
        # print(decoder.decode_32bit_float())

    except AttributeError:
        return ["error decoding"]

    return readings


def read_nitrate1():
    return ["not implemented"]


def open_window():
    layout = [[sg.Text("New Window", key="new")],
              [sg.Multiline(size=(30, 5), key='textbox')]]
    window = sg.Window("Second Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()


lock = threading.Lock()
readings = {}


def read_sensors():
    global refresh_rate
    print("starting reading thread.")
    while True:
        time.sleep(refresh_rate / 1000)
        reading_dict = {}
        for key in sensors:
            reading_dict[key] = json.dumps(sensors[key]())
        q.put(reading_dict)
        print("completed read")


sensors = {"Turbidity sensor 1": read_turbidity1,
           "DO sensor (Desun)": read_do1,
           "DO sensor (Remond)": read_remond_DO,
           "EC sensor 1": read_RMD_EC,
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
    layout.append([sg.Text("_"*30)])

layout.append([sg.Text('Update freq (ms)', size=(18, 1)),
              sg.InputText(key="update_freq", default_text=settings["refresh_rate"])])
layout.append(
    [sg.Text('What you print will display below:                                       ', key="current_monitor_text")])

# layout.append([sg.Output(size=(80, 40), key='-OUTPUT-')]
#               )

layout.append([sg.Button('Update'), sg.Button('Cancel'),
              sg.Button('Start logging', key="log_button")])

window = sg.Window('Sensor readings', layout,
                   element_justification='c', finalize=True)
window['update_freq'].bind("<Return>", "_Enter")

layout2 = [[sg.Multiline(size=(100, 30), key='textbox')]]
window2 = sg.Window("Logging data", layout2, finalize=True)


reading_thread = threading.Thread(target=read_sensors, args=(), daemon=True)
reading_thread.start()

while True:

    event, values = window.read(timeout=200)
    if q.qsize():
        readings = q.get()
        for key in readings:
            window['sensor__'+key].update(readings[key])
            if settings["current_monitor"] == key:
                monitor_data += datetime.datetime.now().isoformat() + " " + \
                    readings[key] + "\n"
                window2["textbox"].update(monitor_data)
                if log_on:
                    log_file.write(monitor_data)

    # print(event, values)
    # print("starting read")
    # for key in sensors:
    #     window['sensor__'+key].update(
    #         json.dumps(sensors[key]()))
    #     if settings["current_monitor"] == key:
    #         print(json.dumps(sensors[key]()))
    #         sg.Print(json.dumps(sensors[key]()))
    # print("finishing read")
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    # print(event)

    if "__button" in event:
        settings["current_monitor"] = event[:-8]
        window["current_monitor_text"].update(
            "Currently monitoring " + event[:-8])
        monitor_data = ""

    if "update_freq_Enter" in event:
        if values['update_freq'].isnumeric():
            settings["refresh_rate"] = int(values['update_freq'])
            refresh_rate = settings['refresh_rate']
        else:
            window['update_freq'].update(settings["refresh_rate"])

    if "log_button" in event:
        if not settings["current_monitor"]:
            sg.Popup("No sensor currently being monitored")
            continue
        log_file = open(datetime.datetime.now().isoformat()[0:16] +
                        settings["current_monitor"] + ".txt", "a")
        log_on = not log_on

        window["log_button"].update(('Logging off', 'Logging on')[log_on])
window.close()
if log_on:
    log_file.close()
