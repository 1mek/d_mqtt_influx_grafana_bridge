#!/bin/ash

set -e

#bro (bridge mqtt->influxdb) user.
mosquitto_passwd -b /mosquitto/config/mosquitto.passwd bro AC5sNQh5aJRc

if [ ! -f addusers ]
then
  echo "$0: File for extra users not found."
  exit 1
fi

# Convert the password file.
mosquitto_passwd -U /addusers
cat /addusers >> /mosquitto/config/mosquitto.passwd



exec "$@"
