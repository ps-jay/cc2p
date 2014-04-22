#!/bin/env python26

import calendar
import datetime
import sqlite3
import sys
import time

values = {
#    'phase1': [],
#    'phase2': [],
#    'phase3': [],
    'power': [],
}

kWhs = {
#    'phase1': 0,
#    'phase2': 0,
#    'phase3': 0,
    'power': 0,
}

if len(sys.argv) == 1:
    print "Last 1 hour"
    end = calendar.timegm(time.gmtime())
    start = end - 3600
else:
    start = datetime.datetime(2013, 05, int(sys.argv[1]), 15, 0)
    end = datetime.datetime(2013, 05, int(sys.argv[1]), 20, 0)
    print "From %s to %s (UTC)" % (start, end,)
    start = calendar.timegm(start.timetuple())
    end = calendar.timegm(end.timetuple())

database = sqlite3.connect('/opt/cc2p.data/power.sqlite')
cursor = database.cursor()

# Create tables
for value in values:
    cursor.execute('''SELECT * FROM %s WHERE timestamp > ? AND timestamp <= ?''' % value, (start, end,))

    values[value] = cursor.fetchall()

    for i in values[value]:
        kWhs[value] = kWhs[value] + i[1]
    
    samples = len(values[value])
    hours = (end - start) / float(3600)

    kWhs[value] = (float(kWhs[value]) / float(samples)) / float(1000)

cursor.close()
database.close()

total = 0

for kWh in kWhs:
    total = total + kWhs[kWh]

#print kWhs
print "From %s samples, over %s:%02d hours & minutes: \n" \
    " -> the average kWh value is: %.2fkWh \n" \
    " -> kWh's consumed over the period: %.1fkWhs" % (
        samples,
        int(hours),
        int(hours * 60) % int(60),
        total,
        total * hours,
    )
