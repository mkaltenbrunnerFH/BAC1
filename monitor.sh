#!/bin/sh

INT="wlx00c0ca9785e7"
MONINT="wlan0mon"
CHANNEL="6"

if [ $# -eq 0 ]
then
  echo "Use -start to put Antenna in Monitor mode"
  echo "Use -stop to stop Monitor mode"
elif [ $1 = "-start" ]
then
  echo "setting $INT to monitor mode..."
  sudo airmon-ng start $INT $CHANNEL > output.txt
  sudo ifconfig $MONINT up > /dev/null
elif [ $1 = "-stop" ]
then
  echo "stopping monitor mode for $MONINT..."
  sudo airmon-ng stop $MONINT > /dev/null
else
  echo "Invalid Args"
fi
