import machine
from stm32_alphabot_v2 import AlphaBot_v2
from stm32_ssd1306 import SSD1306, SSD1306_I2C
import neopixel

alphabot = AlphaBot_v2()
oled = SSD1306_I2C(128, 64, alphabot.i2c, addr=alphabot.getOLEDaddr())

d0 = machine.Pin('D0', machine.Pin.OUT)
d1 = machine.Pin('D1', machine.Pin.OUT)

npAlphabot0 = neopixel.NeoPixel(d0, 4)
npAlphabot1 = neopixel.NeoPixel(d1, 4)

# npAlphabot0[0] = (255, 0, 0)
# npAlphabot0.write()
# npAlphabot1[0] = (255, 0, 0)
# npAlphabot1.write()

# for i in range(4):
#     npAlphabot0[i] = (0, 0, 0)
#     npAlphabot1[i] = (0, 0, 0)
#     npAlphabot0.write()
#     npAlphabot1.write()
        
ledsOn = False

import uasyncio as asyncio
import RobotBleServer

robotName = 'PLPQGLPL'

def onMsgToRobot(data:str):
  # oled.text(data, 0, 0)
  # oled.show()

    ls = 0
    rs = 0

    if('u' in data):
        ls += 50
        rs += 100
    if('d' in data):
        ls -= 50
        rs -= 100
    if('l' in data):
        ls *= 0.5
        if(ls==0): 
            ls=-20
            rs=50
    if('r' in data):
        rs *= 0.5
        if(rs==0): 
            ls=20
            rs=-50
	if('0' in data):
		ls = 0
		rs = 0
	if('1' in data):
		ls = 40
		rs = 40
	if ('2' in data):
		ls = 20
		rs = 20

    if('s' in data):
        # oled.text(ledsOn, 0, 0)
        # oled.show()

        # ledsOn = not ledsOn
        
        if(npAlphabot0[0][0] == 255):
            npAlphabot0[0] = (0, 0, 0)
            npAlphabot0.write()
            npAlphabot1[0] = (0, 0, 0)
            npAlphabot1.write()
        else:
            npAlphabot0[0] = (255, 0, 0)
            npAlphabot0.write()
            npAlphabot1[0] = (255, 0, 0)
            npAlphabot1.write()

    alphabot.setMotorLeft(ls)
    alphabot.setMotorRight(rs)


async def robotMainTask(bleConnection):
    """Main function for robot activities
    :param bleConnection: object to check BLE connection and send messages"""
    while True:
        await asyncio.sleep(0.1)
        if not bleConnection.connection: continue


# Run tasks
async def main():
    print('Start main')
    bleConnection = RobotBleServer.RobotBleServer(robotName=robotName, onMsgReceived=onMsgToRobot)
    asyncio.create_task(robotMainTask(bleConnection))
    await bleConnection.communicationTask()

asyncio.run(main())