#!/usr/bin/env python

# XML lib
from currentcost import Packet
# pySerial
import serial

#Config
serial_port = '/dev/ttyUSB1'
log_dir = '/home/jp/currentcost/'

conn = serial.Serial(serial_port)
# Every six seconds, we get a chunk of XML terminated by a newline
while 1:
    # Parse and get data
    p = Packet(conn, log_dir)

    # Log, save raw etc.
    p.log_all()
