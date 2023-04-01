#!/usr/bin/bash

drive=$1
if [[($drive == "")]]; then
  echo missing drive
  exit 1
fi

cp -r aioble $drive/
cp RobotBleServer.py $drive/
cp mainRobot.py $drive/main.py
