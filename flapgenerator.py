#! /usr/bin/python

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
from argparse import ArgumentParser
from ipaddress import ip_network


def get_announce(nlri, attributes):
    exastring = f'announce route {nlri} next-hop self'
    for attr in attributes:
        exastring = exastring + " " + attr + " " + attributes[attr]
    return exastring+'\n'


def routeflap(args):
    if args.flapping > args.routes:
        print('Number of routes has to be greater or equal to number of flapping routes.')
        sys.exit(1)

    setup = {
        'delay_start': args.delaystart,
        'delay_flap': args.delayflap,
        'interval_flap': args.intervalflap,
        'routes': {},
        'flapping': []
    }

    routes4 = {}
    if args.ipv4network != '':
        net4 = ip_network(args.ipv4network).hosts()
        for i in range(0, args.routes):
            routes4[str(net4.__next__())+'/32'] = {}
        pick_route = 0
        for i in range(0, args.flapping):
            setup['flapping'].append(list(routes4.keys())[pick_route])
            pick_route = (pick_route + 3) % len(routes4)

    routes6 = {}
    if args.ipv6network != '':
        net6 = ip_network(args.ipv6network)
        if net6.prefixlen >= 64:
            print('IPv6 network has to be bigger than /64!')
            sys.exit(1)

        subnet = net6.hosts().__next__() - 1
        for i in range(0, args.routes):
            if ip_network(str(subnet)+'/64').hosts().__next__() not in net6:
                print('IPv6 network not big enough to create requested number of subnets.')
                sys.exit(1)
            routes6[str(subnet)+'/64'] = {}
            subnet = subnet + 2**64

        pick_route = 0
        for i in range(0, args.flapping):
            setup['flapping'].append(list(routes6.keys())[pick_route])
            pick_route = (pick_route + 3) % len(routes6)

    setup['routes'] = {**routes4, **routes6}
    del net4, net6, i, subnet, pick_route, routes4, routes6

    with open("/tmp/flapgenerator_setup.json", "w") as f:
        f.write(json.dumps(setup, indent=4))

    print("setup.json written to file.")

def create_args_parser():
    parser = ArgumentParser(description='BGP flap generator')
    s = parser.add_subparsers()

    parser_routeflap = s.add_parser('routeflap', help='create a peer with routeflaps')
    parser_routeflap.add_argument('-r', '--routes', default=10, help='number of (not flapping) routes to announce (for each of IPv4 and IPv6)')
    parser_routeflap.add_argument('-f', '--flapping', default=5, help='number of flapping routes to announce, has to be <= -r (for each of IPv4 and IPv6)')
    parser_routeflap.add_argument('-4', '--ipv4network', default='', help='IPv4 network to use for address generation')
    parser_routeflap.add_argument('-6', '--ipv6network', default='', help='IPv6 network to use for subnet generation')
    parser_routeflap.add_argument('-ds', '--delaystart', default=0, help='time to wait before anything is announced')
    parser_routeflap.add_argument('-df', '--delayflap', default=2, help='time to wait after initial announcements before flapping starts')
    parser_routeflap.add_argument('-if', '--intervalflap', default="500ms", help='time between switching state of flapping routes')
    parser_routeflap.set_defaults(func=routeflap)

    return parser

if __name__ == '__main__':
    parser = create_args_parser()
    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    args.func(args)
