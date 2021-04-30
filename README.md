Little script to test and program modbus id numbers in to the Chinese water sensors.
Currently uses ttyUSB0 for the USB dongle, which seems to work. To find out the address
of most recent USB device, use `dmesg | grep tty`

The device ID is held in register 0x19. This can be written to to change the ID. If ID
is changed, you use unit=xxx, where xxx is the new unit number. 

Eventually each sensor we are using needs to have a specific ID that we assign it, 
e.g. chlorine sensor = 1, pH sensor = 2.

