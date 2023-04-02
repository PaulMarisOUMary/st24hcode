# python -m serial.tools.list_ports
# python mainPcTestBLE.py -p <port com>

# In this example, PC will send some messages to robot,
# and verify it receives same messages from robot
# Note: if message from PC to robot exceeds 18 characters, it will be split in
# several BLE messages, then merged at robot side to get original message
# Note: message from robot to PC shall not exceed 18 characters

import sys
import time
import argparse
import ComWithDongle
import keyboard


# This is the name your PC will search for, in advertising.
# In order not to connect on a wrong robot, you shall change this name;
# other teams shall not use same name.
# On robot side, you shall also use this new name for robot to send in advertising
robotName = "PLPQGLPL"

randCharRange = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

recentlySent = []

def onMsgFromRobot(data:str):
	"""Function to call when a message sent by robot is received
	:param data: message"""
	print('msg', data, flush=True)
	if data in recentlySent:
		recentlySent.remove(data)
	else:
		print('bad message received', data)
		print('recently sent')
		for s in recentlySent:
			print('  ', s)
		exit(1)

parser = argparse.ArgumentParser(
	description='Script to communicate with STM32WB55 dongle connected on computer')
parser.add_argument('-p', '--portcom', type=str, help='id of com port used')
parser.add_argument('-d', '--debug', action='store_true', help='display debug messages')
parser.add_argument('-l', '--length', type=int, default=16,
	help='number of characters to send over BLE, in each message')
parser.add_argument('-n', '--number', type=int, default=5 , help='number of messages to send over BLE')
args = parser.parse_args()


try:
	print('start main')
	com = ComWithDongle.ComWithDongle(comPort=args.portcom, peripheralName=robotName,
		onMsgReceived=onMsgFromRobot, debug=args.debug)
	print('connected to', robotName)
	while True:
		# car_status, position, orientation, x, y, race_status, counter, timestamp_ns = getRaceData()
		# left, right, yaw = PIDControler(orientation, yaw)

		data = 'n' #''.join([random.choice(randCharRange) for _ in range(args.length)])
		if keyboard.is_pressed('down arrow'):
			data += 'u'
			print('u')
		if keyboard.is_pressed('up arrow'):
			data += 'd'
			print('d')
		if keyboard.is_pressed('left arrow'):
			data += 'l'
			print('l')
		if keyboard.is_pressed('right arrow'):
			data += 'r'
			print('r')
		if keyboard.is_pressed('space'):
			data += 's'
			print('space')
		if keyboard.is_pressed('0'):
			data += '0'
			print('0')
		if keyboard.is_pressed('1'):
			data += '1'
			print('1')
		if keyboard.is_pressed('2'):
			data += '2'
			print('2')


		com.sendMsg(data)

		time.sleep(0.01)
		nbMissing = len(recentlySent)
		lastNbMissing = 0
		while not nbMissing == lastNbMissing:
			time.sleep(2)
			print('missing', recentlySent, flush=True)
			lastNbMissing = nbMissing
			nbMissing = len(recentlySent)
except KeyboardInterrupt:
	pass
com.disconnect()
exit(0)
