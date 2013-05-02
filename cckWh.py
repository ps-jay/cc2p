#!/bin/env python26

import calendar
import sqlite3
import time

values = {
    'phase1': [],
    'phase2': [],
    'phase3': [],
}

kWhs = {
    'phase1': 0,
    'phase2': 0,
    'phase3': 0,
}

end = calendar.timegm(time.gmtime())
start = end - 3600

database = sqlite3.connect('/opt/cc/power.sqlite')
cursor = database.cursor()

# Create tables
for value in values:
    cursor.execute('''SELECT * FROM %s WHERE timestamp > ? AND timestamp <= ?''' % value, (start, end,))

    values[value] = cursor.fetchall()

    for i in values[value]:
        kWhs[value] = kWhs[value] + i[1]
    
    kWhs[value] = float((float(kWhs[value]) / float(len(values[value]))) / 1000)

cursor.close()
database.close()

total = 0

for kWh in kWhs:
    total = total + kWhs[kWh]

print kWhs
print total
