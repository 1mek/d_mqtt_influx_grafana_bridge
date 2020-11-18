#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge
This script receives MQTT data and saves those to InfluxDB.
with docker ENV.
"""

import re
import os
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = os.getenv('BRO_DB_URL', 'localhost')
INFLUXDB_USER = os.getenv('BRO_DB_USER', 'bro')
INFLUXDB_PASSWORD = os.getenv('BRO_DB_PASS', 'sssSDFqQqwe')
INFLUXDB_DATABASE = os.getenv('BRO_DB_NAME', 'mdn_db')

MQTT_ADDRESS = os.getenv('BRO_MQTT_URL', 'localhost')
MQTT_USER = os.getenv('BRO_MQTT_USER', 'bro')
MQTT_PASSWORD = os.getenv('BRO_MQTT_PASS', 'AC5sNQh5aJRc')
MQTT_TOPIC = os.getenv('BRO_TOPIC', 'i/+/+')  # i/sender/[m] || [battery|status|etc]
MQTT_M = os.getenv('BRO_MULTI', 'm')
MQTT_REGEX = 'i/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'mqtt2influx'
MQTT_MULTI = '([^/]+)/([^/]+)'
MQTT_SEPARATOR = ';'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    topic = msg.topic
    payload = msg.payload.decode('utf-8')

    match = re.match(MQTT_REGEX, topic)
    if match:
      location = match.group(1)
      if match.group(2) == MQTT_M:
         pay = payload.split (MQTT_SEPARATOR)
         for i in range (0, len (pay)):
            urk = re.match (MQTT_MULTI, pay[i])
            if urk  :
                location = match.group (1)
                measurement = urk.group (1)
                value = urk.group (2)
                print (location, measurement, value)
                _send_sensor_data_to_db_multi(location,measurement,value)
      else:
         measurement = match.group(2)
         print(location, measurement, payload)
         _send_sensor_data_to_db_multi(location,measurement,payload)

    return None


def _send_sensor_data_to_db_multi(location, measurement, value):
    json_body = [
        {
            'measurement': measurement,
            'tags': {
                'location': location
            },
            'fields': {
                'value': float(value)
            }
        }
    ]
    print(json_body)
    influxdb_client.write_points(json_body)


def _send_sensor_data_to_influxdb(sensor_data):
    json_body = [
        {
            'measurement': sensor_data.measurement,
            'tags': {
                'location': sensor_data.location
            },
            'fields': {
                'value': sensor_data.value
            }
        }
    ]
    influxdb_client.write_points(json_body)


def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('1mek >> MQTT to InfluxDB bridge')
    main()
