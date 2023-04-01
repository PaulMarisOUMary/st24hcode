# to know COM port used when connected on PC:
# python -m serial.tools.list_ports

# in this example, robot will send back to PC all messages received
# Note: message from robot to PC shall not exceed 18 characters

import uasyncio as asyncio
import RobotBleServer

# This is the name your robot will use in advertising.
# In order not to connect on a wrong robot, you shall change this name;
# other teams shall not use same name.
# On PC side, you shall also use this new name for robot you will search for in advertising
robotName = 'myTeamName'

toSend = []

def onMsgToRobot(data:str):
	"""Function to call when a message sent by PC is received
	:param data: message received"""
	#print('msg', data)
	toSend.append(data)

async def robotMainTask(bleConnection):
	"""Main function for robot activities
	:param bleConnection: object to check BLE connection and send messages"""
	while True:
		await asyncio.sleep(0.1)
		if not bleConnection.connection: continue
		# BLE connection is established, we can send messages to PC
		if toSend == []: continue
		while not toSend == []:
			data = toSend.pop(0)
			#print('send', data)
			bleConnection.sendMessage(data)
			print('sent', data)

# Run tasks
async def main():
	print('Start main')
	bleConnection = RobotBleServer.RobotBleServer(robotName=robotName, onMsgReceived=onMsgToRobot)
	asyncio.create_task(robotMainTask(bleConnection))
	await bleConnection.communicationTask()

asyncio.run(main())
