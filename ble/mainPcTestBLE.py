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
import random
import ComWithDongle

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
	# wait BLE connection is established
	com = ComWithDongle.ComWithDongle(comPort=args.portcom, peripheralName=robotName,
		onMsgReceived=onMsgFromRobot, debug=args.debug)
	print('connected to', robotName)
	msgId = 0
	while True:
		data = ''.join([random.choice(randCharRange) for _ in range(args.length)])
		print('send data', len(data), msgId, data, flush=True)
		recentlySent.append(data)
		com.sendMsg(data)
		msgId += 1
		if msgId >= args.number: break
		time.sleep(0.01)
	#all messages sent, wait while we receive some messages
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

def keypressed(key):
    if key == keyboard.Key.space:     
        print('space pressed')
        machine.pin(D0).neopixel(red)
        machine.pin(D1).neopixel(red)
    elif key == keyboard.Key.up:
        print('up pressed')
    elif key == keyboard.Key.down:      
        print('down pressed')
    elif key == keyboard.Key.left:
        print('left pressed')
    elif key == keyboard.Key.right:
        print('right pressed')
    elif key == keyboard.Key.esc:
        print('Escape')
        listener.stop() 

listener = keyboard.Listener(on_press=keypressed)
listener.start()
listener.join()