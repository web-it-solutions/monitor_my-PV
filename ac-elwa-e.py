# imports
from configparser import ConfigParser
from datetime import datetime
from influxdb import InfluxDBClient

import json
import urllib.request

# configuration
config = ConfigParser()
config.read(['_config.ini', '_user.ini'])

# debug mode
debug = config.getboolean('source', 'debug', fallback = False)

# connect to influxDB to persist data
def connectToInfluxDB():
    # influxDB configuration settings with fallback(s)
    influxDatabase = config.get('influxDB', 'database', fallback = 'mypv')
    influxHost = config.get('influxDB', 'host', fallback = '127.0.0.1')
    influxPassword = config.get('influxDB', 'password', fallback = '')
    influxUser = config.get('influxDB', 'user', fallback = '')

    # influxDB port configuratioin has to be an integer
    try:
        influxPort = config.getint('influxDB', 'port', fallback = 8086)
    except ValueError as error:
        print('Error: ' + str(error))
        quit()

    # check validity of influxDB connection concerning host and port only
    try:
        influxDBClient = InfluxDBClient(influxHost, influxPort, influxUser, influxPassword, influxDatabase)
        influxDBClient.ping()
    except Exception as error:
        print('Error connecting to influxDB:')
        print('-> ' + str(error))
        quit()

    return influxDBClient

# converts data for special keys so they have 'correct' values
def convertFieldValues(data):
    for key in data:
        if key in ['temp1', 'ww1target']:
            data[key] = float(data[key])/10

    return data

# collect defined data from AC ELWA-E
def getData():
    ip = config.get('source', 'ip')

    # check for necessary config keys
    if '' == ip:
        print("Required config 'ip' within [source] in config.ini is missing!")
        quit()

    fields = config.get('source', 'fields')
    url = "http://" + ip + "/data.jsn"
    mypvData = json.loads(urllib.request.urlopen(url).read())

    if '' == fields:
        return mypvData

    # collect fields defined in config.ini
    mypvFields = dict()

    for key in mypvData:
        if key in fields:
            mypvFields[key] = mypvData[key]

    return mypvFields

# write collected data to defined influxDB
def writeDataToInfluxDB(fields):
    measurement = config.get('influxDB', 'measurement', fallback = 'ac_elwa_e')
    points = [{
        'fields': fields,
        'measurement': measurement
    }]

    try:
        influxDBClient.write_points(points, time_precision = 's')
    except Exception as error:
        print('Error connecting to influxDB:')
        print('-> ' + str(error))
        quit()

# collect and persist data
influxDBClient = connectToInfluxDB()
data = getData()
data = convertFieldValues(data)
writeDataToInfluxDB(data)

if True == debug:
    print('Debug: AC ELWA-E data:')

    for key in sorted(data):
        print('-> ' + key + ': ' + str(data[key]))
