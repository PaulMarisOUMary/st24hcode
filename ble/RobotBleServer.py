# to know COM port used when connected on PC:
# python -m serial.tools.list_ports

import sys
sys.path.append("")
from micropython import const
import aioble
import bluetooth
import struct

_SERVICE_UUID = bluetooth.UUID(0x1234)
_CHAR_UUID = bluetooth.UUID(0x1235)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

_COMMAND_DONE = const(0)
_COMMAND_SENDDATA = const(1)
_COMMAND_SENDCHUNK = const(2)  # send chunk of data, use _COMMAND_SENDDATA for last chunk

class RobotBleServer:
	"""Class to manage connection with BLE"""
	def __init__(self, robotName:str, onMsgReceived):
		""":param robotName: name to use in advertising
		:param onMsgReceived: function to call when a message is received"""
		self.robotName = robotName
		self.onMsgReceived = onMsgReceived
		# Register GATT server.
		service = aioble.Service(_SERVICE_UUID)
		self.characteristic = aioble.Characteristic(service, _CHAR_UUID, write=True, notify=True)
		aioble.register_services(service)
		self.connection = None

	def sendMessage(self, msg:str):
		"""Send a message over BLE
		:param msg: message to send"""
		self.characteristic.notify(self.connection, struct.pack("<B", _COMMAND_SENDDATA) + msg)

	async def bleTask(self):
		"""Loop to wait for incoming messages over BLE.
		When a received message is complete, call function defined in self.onMsgReceived
		When BLE connection is closed, stop this function"""
		try:
			with self.connection.timeout(None):
				dataChunk = ''
				msgId = 0
				while True:
					await self.characteristic.written()
					msg = self.characteristic.read()
					#self.characteristic.write(b"")

					if len(msg) < 3:
						continue

					# Message is <command><seq><data>.
					command = msg[0]
					op_seq = int(msg[1])
					msgData = msg[2:].decode()
					#print('CMD=', command)

					if command == _COMMAND_SENDCHUNK:
						dataChunk += msgData
						#print('received chunk', msgData, '=>', dataChunk)
					elif command == _COMMAND_SENDDATA:
						data = dataChunk + msgData
						print('received:', len(data), msgId, data)
						dataChunk = ''
						self.onMsgReceived(data)
						msgId += 1
		except aioble.DeviceDisconnectedError:
			print('disconnected BLE')
			return

	async def communicationTask(self):
		"""Loop to advertise and wait for connection.
		When connection is established, start task to read incoming messages"""
		while True:
			print("Waiting for connection")
			self.connection = await aioble.advertise(
				_ADV_INTERVAL_MS,
				name=self.robotName,
				services=[_SERVICE_UUID],
			)
			print("Connection from", self.connection.device)
			await self.bleTask()
			await self.connection.disconnected()
			self.connection = None
	
