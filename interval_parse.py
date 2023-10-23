#! /usr/bin/env python3

import sys
from statistics import mean

min_int = None
max_int = None
intervals = []

count = 1
try:
    for line in sys.stdin:
        try:
            timeStr = line.split(" ")[1]
            time_ms = timeStr.split(".")[1]
            hms = timeStr.split(".")[0].split(":")
            sec = int(hms[0]) * 60 * 60 + int(hms[1]) * 60 + int(hms[2])
            time = sec + (int(time_ms)/1000000)
            print(f"{count};{time}", flush=True)
            count += 1
            if min_int is None or time < min_int:
                min_int = time
            if max_int is None or time > max_int:
                max_int = time
            intervals.append(time)
        except Exception as e:
            pass
except KeyboardInterrupt:
    pass

if len(sys.argv) > 1 and sys.argv[1] == '--stats':
    avg_int = mean(intervals)
    print('')
    print(f"MIN: {min_int}s = {min_int*1000}ms")
    print(f"AVG: {avg_int}s = {avg_int*1000}ms")
    print(f"MAX: {max_int}s = {max_int*1000}ms")
