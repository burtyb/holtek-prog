#!/usr/bin/env python3

#############################################
##                                         ##
## Chris Burton (c) 2019-11-11             ##
##  Chris@8086.net                         ##
##                                         ##
#############################################
##                                         ##
## Programmer for Holtek HT42B534          ##
##  USB to UART Bridge IC                  ##
##                                         ##
#############################################
##                                         ##
## https://github.com/burtyb/HT42B534-prog ##
##                                         ##
#############################################

import os
import sys
import argparse
import time

import usb.core
import usb.util


def validate_pid(pid):
	try:
		pid = int(pid, 0) # Convert from hex if needed
	except ValueError:
		raise argparse.ArgumentTypeError('PID must be an integer 0-65535')
	if (pid < 0) or (pid > 65535):
		raise argparse.ArgumentTypeError('PID must be an integer 0-65535')
	return pid

def validate_vid(vid):
	try:
		vid = int(vid, 0) # Convert from hex if needed
	except ValueError:
		raise argparse.ArgumentTypeError('VID must be an integer 0-65535')
	if (vid < 0) or (vid > 65535):
		raise argparse.ArgumentTypeError('VID must be an integer 0-65535')
	return vid

def validate_manu(m):
	if (len(m) > 16) or (len(m) < 1):
		raise argparse.ArgumentTypeError('Manufacturer must be between 1-16 characters')
	return m

def validate_desc(d):
	if (len(d) > 32) or (len(d) < 1):
		raise argparse.ArgumentTypeError('Manufacturer must be between 1-32 characters')
	return d

def validate_serial(s):
	if (len(s) > 4) or (len(s) < 1):
		raise argparse.ArgumentTypeError('Serial must be between 1-4 characters')
	return s

p = argparse.ArgumentParser(description='Holtek HT42B534 Programmer')
p.add_argument('vid', help='Vendor ID to change', type=validate_vid)
p.add_argument('pid', help='Product ID to change', type=validate_pid)
p.add_argument('-v', '--setvid', help='Set Vendor ID', default='1241', type=validate_vid)
p.add_argument('-p', '--setpid', help='Set Product ID', default='46388', type=validate_pid)
p.add_argument('-H', '--hwflow', help='Enable Hardware Flow Control', action='store_true')
p.add_argument('-W', '--wake', help='Enable Remote Wake', action='store_true')
p.add_argument('-L', '--loop', help='Continous program loop' , action='store_true')
p.add_argument('-I', '--inc', help='When looping increment serial', action='store_true')
p.add_argument('-m', '--manufacturer', help='Set Manufacturer', default='HOLTEK', type=validate_manu)
p.add_argument('-d', '--description', help='Set Description', default='USB TO UART BRIDGE', type=validate_desc)
p.add_argument('-s', '--serial', help='Set Serial', default='0000', type=validate_serial)
p.add_argument('-P', '--pad', help='Zero pad serial to 4 characters', action='store_true')
args = p.parse_args()

# Zero pad serial if needed
if args.pad:
	args.serial = args.serial.zfill(4)

def program():
	device = usb.core.find(idVendor=args.vid, idProduct=args.pid)

	if not device:
		print(" Device not found")
	else:
		print(" Device found")
		if device.is_kernel_driver_active(0):
			try:
				device.detach_kernel_driver(0)
			except usb.core.USBError as e:
				device.detach_kernel_driver(0)
				sys.exit("Could not detatch kernel driver: %s" % str(e))

		try:
			device.set_configuration()
			device.reset()
		except usb.core.USBError as e:
			sys.exit("Could not set configuration: %s" % str(e))

		report = bytearray(512)

		report[0] = 0x62	# b
		report[1] = 0x72	# r
		report[2] = 0x69	# i
		report[3] = 0x64	# d
		report[4] = 0x67	# g
		report[5] = 0x65	# e
		report[6] = 0x2d	# -
		report[7] = 0x75	# u

		device.ctrl_transfer(0x21,9,0x0300,0x0002,report)

		report = bytearray(512)

		report[0] = 0x01

		# Vendor ID
		report[2] = (args.setvid&0xFF)	# Low
		report[3] = (args.setvid>>8)	# High

		# Product ID
		report[4] = (args.setpid&0xFF)	# Low
		report[5] = (args.setpid>>8)	# High

		# H/W Flow control
		if args.hwflow:
			report[0x80] = 0x01

		# Remote Wakeup
		if args.wake:
			report[0x82] = 0x01

		# Manufacturer
		report[0x06] = (len(args.manufacturer)+1)*2 # Length
		report[0x07] = 0x03
		index = 0
		for c in args.manufacturer:
			report[0x08+(index*2)] = ord(args.manufacturer[index])
			index=index+1

		# Product description
		report[0x28] = (len(args.description)+1)*2 # Length
		report[0x29] = 0x03
		index = 0
		for c in args.description:
			report[0x2A+(index*2)] = ord(args.description[index])
			index=index+1

		# Serial
		report[0x6A] = (len(args.serial)+1)*2 # Length
		report[0x6B] = 0x03
		index = 0
		for c in args.serial:
			report[0x6C+(index*2)] = ord(args.serial[index])
			index=index+1

		report[0xE2] = 0x01

		device.ctrl_transfer(0x21,9,0x0300,0x0002,report)

		print(" Programming completed (Serial: {})".format(args.serial))

		# Wait for unplug
		print(" Waiting for unplug")
		while True:
			try:
				device.ctrl_transfer(0x21, 0x01, 0x300, 0x0002, report)

			except Exception as  e:
				if e.errno == 19: # No such device
					break
			time.sleep(1)

if args.loop:
	print("Waiting for device")
	while True:
		device = usb.core.find(idVendor=args.vid, idProduct=args.pid)
		if not device:
			time.sleep(1)
		else:
			program()
			if args.inc:
				if args.pad:
					args.serial = str(int(args.serial)+1).zfill(4)
				else:
					args.serial = str(int(args.serial)+1)
			print("Waiting for device")
		
else:
	program()
