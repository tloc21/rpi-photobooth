#!/bin/bash

tsdate=$(date +%Y-%m-%d)
tstime=$(date +%H%M%S)
echo ${tsdate}
sudo mkdir -p /media/usb/Photos/${tsdate}/${tstime}
cp /home/pi/photobooth_images/*.jpg /media/usb/Photos/${tsdate}/${tstime}
