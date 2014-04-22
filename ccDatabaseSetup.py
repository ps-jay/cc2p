#!/bin/env python

import sqlite3

values = {
    'temperature': 'REAL',
    'power': 'INTEGER',
#    'phase2': 'INTEGER',
#    'phase3': 'INTEGER',
}

database = sqlite3.connect('/opt/cc2p.data/power.sqlite')
cursor = database.cursor()

# Create tables
for value in values:
    cursor.execute('''CREATE TABLE %s
        (timestamp INTEGER PRIMARY KEY, value %s, uploaded INTEGER)''' % (value, values[value],))
    cursor.execute('''CREATE INDEX %s_ul ON %s (uploaded)''' % (value, value))

    database.commit()

cursor.close()
database.close()
