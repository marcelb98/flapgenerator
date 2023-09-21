#! /bin/bash

curl http://172.31.196.81:8080/start?comment=flap_1ms

env exabgp.api.ack=false exabgp.cache.attributes=false exabgp exa.config

