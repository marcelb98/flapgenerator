#! /usr/bin/env python

#    Copyright 2023 Marcel Beyer
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import sys
import time

# Helper function to bring route (NLRI + attributes) in format needed by ExaBGP
def get_announce(nlri, attributes):
    exastring = f'announce route {nlri} next-hop self'
    for attr in attributes:
        exastring = exastring + " " + attr + " " + attributes[attr]
    return exastring+'\n'

# Helper function which takes integer in seconds or string with suffix s, ms, us and returns integer in seconds
def parse_time_str(time):
    time_orig = time
    if isinstance(time, int):
        pass
    elif time.isnumeric():
        time = int(time)
    elif time.endswith("us"):
        time = int(time[:-2]) / 1000000
    elif time.endswith("ms"):
        time = int(time[:-2]) / 1000
    elif time.endswith("s"):
        time = int(time[:-1])
    else:
        print(f"Could not parse time {time_orig}.")
        sys.exit(1)
    return time

# Read setup which contains all routes and list of routes to flap
with open("/tmp/flapgenerator_setup.json", "r") as f:
    try:
        setup = json.load(f)
    except ValueError:
        print("Could not pares setup.yaml!")
        sys.exit(1)
routes = setup['routes']
flapping = setup['flapping']

# prepare exabgp commands for all routes once
routes_exa = {}
for route in routes:
    routes_exa[route] = get_announce(route, routes[route])
flapping_exa = {}
for route in flapping:
    flapping_exa[route] = f"withdraw route {route} next-hop self\n"

# free up memory
del routes, flapping

# wait requested start time
if 'delay_start' in setup:
    time.sleep(parse_time_str(setup['delay_start']))

# initial announce of all routes
for route in routes_exa:
    sys.stdout.write(routes_exa[route])
sys.stdout.flush()

# wait with flapping if requested
if 'delay_flap' in setup:
    time.sleep(parse_time_str(setup['delay_flap']))

# make sure interval is set correct
if 'interval_flap' not in setup:
    interval = '1s'
else:
    interval = setup['interval_flap']
interval = parse_time_str(interval)

# now we start to flap
announce = False
while True:
    for route in flapping_exa:
        if announce:
            sys.stdout.write(routes_exa[route])
        else:
            sys.stdout.write(flapping_exa[route])
    sys.stdout.flush()

    announce = not announce
    time.sleep(interval)
