#! /usr/bin/env python3

import sys

count = 1
for line in sys.stdin:
    try:
        timeStr = line.split(" ")[1]
        time_ms = timeStr.split(".")[1]
        hms = timeStr.split(".")[0].split(":")
        sec = int(hms[0]) * 60 * 60 + int(hms[1]) * 60 + int(hms[2])
        time = sec + (int(time_ms)/1000000)
        print(f"{count};{time}", flush=True)
        count += 1
    except Exception as e:
        pass
