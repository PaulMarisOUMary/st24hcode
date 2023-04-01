import sys
sys.path.append("")
from micropython import const
import json
import uasyncio as asyncio
import aioble
import bluetooth
import struct

_SERVICE_UUID = bluetooth.UUID(0x1234)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x1235)

MAX_MSG_DATA_LENGTH = const(18)

_COMMAND_DONE = const(0)
_COMMAND_SENDDATA = const(1)
_COMMAND_SENDCHUNK = const(2)  # send chunk of data, use _COMMAND_SENDDATA for last chunk

class ManageDongle:
	def __init__(self, device):
		self._device = device
		self._connection = None
		self._seq = 1

	async def connect(self):
		try:
			print("Connecting to", self._device)
			self._connection = await self._device.connect()
		except asyncio.TimeoutError:
			print("Timeout during connection")
			return

		try:
			print("Discovering...")
			service = await self._connection.service(_SERVICE_UUID)
			#uuids = []
			#async for char in service.characteristics():
			#	uuids.append(char.uuid)
			#print('uuids', uuids)
			self._characteristic = await service.characteristic(_CHARACTERISTIC_UUID)
		except asyncio.TimeoutError:
			print("Timeout discovering services/characteristics")
			return

		self.sendDictToCom({'type':'connected'})
		asyncio.create_task(self.readFromBle())

	async def _command(self, cmd, data):
		send_seq = self._seq
		await self._characteristic.write(struct.pack("<BB", cmd, send_seq) + data)
		print('sent packet num', send_seq)
		self._seq += 1
		return send_seq
	
	async def readFromBle(self):
		while True:
			read = await self._characteristic.notified()
			# message format is <command><data>
			cmd = read[0]
			print('received from BLE', read)
			if cmd == _COMMAND_SENDDATA:
				# message to send to computer over COM port
				msg = read[1:].decode()
				self.sendDictToCom({'type':'msgFromBle', 'string':msg})

	async def sendData(self, data):
		while len(data) > MAX_MSG_DATA_LENGTH:
			chunk = data[:MAX_MSG_DATA_LENGTH]
			await self._command(_COMMAND_SENDCHUNK, chunk.encode())
			data = data[MAX_MSG_DATA_LENGTH:]
		await self._command(_COMMAND_SENDDATA, data.encode())
		self.sendDictToCom({'type':'sentMessage'})
	
	async def disconnect(self):
		if self._connection:
			await self._connection.disconnect()

	def sendDictToCom(self, data:dict):
		print(json.dumps(data))

async def main():
	print('start dongle')
	while True:
		try:
			line = input()
		except KeyboardInterrupt:
			# when ctrl-C is sent to dongle, we receive a KeyboardInterrupt
			sys.exit(0)
		#print('dongle received:', line)
		receivedMsgDict = json.loads(line)
		if receivedMsgDict['type'] == 'connect':
			# => start BLE scan and connect on this peripheral
			peripheralName = receivedMsgDict['name']
			async with aioble.scan(5000, 30000, 30000, active=True) as scanner:
				async for result in scanner:
					print('scan', result.name(), result.rssi, result.services())
					if result.name() == peripheralName and _SERVICE_UUID in result.services():
						device = result.device
						break
				else:
					print("Server not found")
					return

			client = ManageDongle(device)
			await client.connect()
		elif receivedMsgDict['type'] == 'disconnect':
			await client.disconnect()
		elif receivedMsgDict['type'] == 'msg':
			await client.sendData(receivedMsgDict['string'])
		else:
			print('unknown message type', receivedMsgDict)
	await client.disconnect()

asyncio.run(main())
