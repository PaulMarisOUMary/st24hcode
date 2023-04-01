# BLE example
Here is an example of driver to send messages using BLE

# Setup on robot (or other BLE advertiser)
Copy following files to robot
* aioble/*
* RobotBleServer.py
* mainRobot.py (to rename as main.py)
You can use script toRobot.sh for that, for example when run from a Windows git bash,
if robot is connected on drive D:, you can run
> ./toRobot.sh /d

# Setup on USB dongle
Copy following files to robot
* aioble/*
* mainDongle.py (to rename as main.py)
You can use script toDongle.sh for that, for example when run from a Windows git bash,
if dongle is connected on drive E:, you can run
> ./toDongle.sh /e

# Setup on computer
You need pyserial module for python. You can install it using command
> python -m pip install pyserial
or if a proxy is required
> python -m pip install --proxy <http proxy parameter> pyserial
Then run following command
  
> python mainPcTestBLE.py --portcom <com port used by dongle>

To know COM port to use as argument, run following command before and after dongle connection:
>  python -m serial.tools.list_ports
Port in second result but not in first result is port used by dongle.

# setup for multiple robots alive at same time
In order for your PC to connect on your robot, and not to connect on another robot
(or other teams not to connect on your robot), each robot shall advertise a different name.
Name of robot uses in advertising is defined in file mainRobot.py, in line
> robotName = 'myTeamName'
Name of robot to search and connect on is defined in file mainPcTestBLE.py, in line
> robotName = 'myTeamName'
You shall change these 2 lines, using another value than "myTeamName"
