# Monitoring AC ELWA-E
Gets data of a my-PV AC ELWA-E heating element via JSON API by a python script and sends it to an InfluxDB.

## Description
The script collects the data the JSON API provides (see below), manipulates it if necessary and afterwards sends it to an InfluxDB. This data can be used to be visualized e.g. by Grafana to display it in panels/dashboards.

To collect the data regularly (I recommend at least every minute), you can decide yourself how to trigger the script, e.g.:
- by inserting it into native `crontab` on a linux machine
- by using a custom scheduled task on a NAS like Synology or Qnap
- any other way you like which fits your needs

## Requirements
- python (3.x)
- InfluxDB (1.8.x)

## Usage
Download or clone this repository into any folder, adjust the `_user.ini` file, setup InfluxDB as described below and call the script:
- local/relative from within the folder: `python3 ac-elwa-e.py`
- absolute with path to python executable: `/usr/bin/python3 /my-folder/monitor_my-PV/ac-elwa-e.py`

### Configuration
If no `_user.ini` is present, the default configuration will be used:
```
[influxDB]
# Name of the database (default: mypv)
#database =
# Host for the connection - IP or hostname (default: 127.0.0.1)
#host =
# Measurement where data is stored (default: ac_elwa_e)
#measurement =
# Password for the connection (default: empty)
#password =
# Port for the connection (default: 8086)
#port =
# User for the connection (default: empty)
#user =

[source]
# Set to True to get some debug output in CLI
debug = False
# Define fields (comma separated) which data should be collected - leave blank to collect all (see README.md for available fields)
fields = m0sum, power, status, surplus, temp1, ww1target
# IP for connection to AC ELWA-E (required)
ip =
```
#### Default values (for better readability)
```
[influxDB]
database = mypv
host = 127.0.0.1
measurement = ac_elwa_e
password =
port = 8086
user =

[source]
debug = False
fields = m0sum, power, status, surplus, temp1, ww1target
ip =
```
Each of these values can be overriden by taking that part into the `_user.ini` file located in the same folder as the `_config.ini`. So if you like to change the name of the database, use credentials and collect all possible data:
```
[influxDB]
database = energy_mypv
password = myPassword
user = myUser

[source]
fields = 
ip = 0.0.0.0
```
As you have to specify at least the IP address of your heating element for a working setup, I absolutely recommend it to go this way.

## Setup
This is ajust a suggestion how a setup could look like. Feel free to adjust it to your needs or prerequisites. I already use Grafana to visualize data, therefore the docker image is mentioned down below. 

### InfluxDB
- Official docker image of [influxdb:1.8](https://hub.docker.com/layers/library/influxdb/1.8/images/sha256-c436689dc135f204734d63b82fd03044fa3a5205127cb2d1fa7398ff224936b1?context=explore)
  - map local port 8086 to container port 8086
  - bind volume to store data on local device `/path/to/local/folder:/var/lib/influxdb`
  - create database `mypv` (database has to exist, will not be created by this script -> `CREATE DATABASE mypv` - see [Testing](#Testing)
- Official docker image of [grafana/grafana:latest](https://hub.docker.com/layers/grafana/grafana/latest/images/sha256-f5518c6c6392bb767813b78d474ed3a228ca0673f1867770d8fd312067abc558?context=explore)
  - map local port 3000 to container port 3000
  - bind volume to store data on local device `/path/to/local/folder:/var/lib/grafana`

## Testing
Log into you InfluxDB to check whether the data is stored correctly. If you use it within a docker image, you need to SSH into the container first - otherwise skip first step:
1. `docker exec -it <INFLUXDB_CONTAINER_NAME> bash`
2. `influx`
3. `SHOW DATABASES`
   - if there is no database named `mypv` you must create it: `CREATE DATABASE mypv`
4. `USE mypv`
5. `SHOW MEASUREMENTS`
   - there should be exactly one measurement named `ac_elwa_e` after executing the script for the first time if you use the default configuration
6. `SELECT * FROM ac_elwa_e ORDER BY time LIMIT 1`
   - depending on how many fields you collect, you will see x values (4 if you use the default configuration) with a timestamp when they were collected
7. `SHOW FIELD KEYS FROM ac_elwa_e`
   - show types of collected fields (float, integer, string)

## Status
I use this script to monitor my heating element once a minute via `task scheduler` on a Synology NAS DS720+. Grafana and InfluxDB are running in a docker container each. 

### Roadmap/Still to come
- Grafana panels & dashboards
- Usage of tags within InfluxDB

# AC ELWA-E
The data is provided via a JSON API which you can call via `http://<IP>>/data.jsn`. The following fields are provided by a device with the following firmware version (`fwversion`): 00204.03.

Following a list of all fields of my device (alphabetically ordered, with explanations of fields):
- blockactive
- boostactive
- boostpower
- cloudstate
- ctrlstate
- cur_dns
- cur_gw
- cur_ip
- cur_sn
- debug_ip
- device
- ecarboostctr
- ecarstate
- fwversion
- legboostnext
- loctime
- m0bat
- m0l1
- m0l2
- m0l3
- m0sum (`integer`: feedb-in point in [W])
- m1devstate
- m1l1
- m1l2
- m1l3
- m1sum
- m2devstate
- m2l1
- m2l2
- m2l3
- m2soc
- m2state
- m2sum
- m3devstate
- m3l1
- m3l2
- m3l3
- m3soc
- m3sum
- m4devstate
- m4l1
- m4l2
- m4l3
- m4sum
- meter1_id
- meter1_ip
- meter2_id
- meter2_ip
- meter3_id
- meter3_ip
- meter4_id
- meter4_ip
- meter5_id
- meter5_ip
- meter6_id
- meter6_ip
- mss10
- mss11
- mss2
- mss3
- mss4
- mss5
- mss6
- mss7
- mss8
- mss9
- power (`integer`: power used in [W])
- status (`integer`: Standby[3]|Heating[2])
- surplus (`integer`: meter + battery charging in [W])
- temp1 (`float`: current water temperature)
- tempchip
- unixtime
- ww1target (`float`: target water temperature)

If anyone has a tip for me on where to find official data on what each field means, feel free to contact me!
