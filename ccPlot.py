#!/bin/env python

import matplotlib.pyplot as plt
import os
import sqlite
import sys
import time

values = {
    'temperature': [],
    'phase1': [],
    'phase2': [],
    'phase3': [],
}

points = {
    'temperature': '',
    'phase1': '',
    'phase2': '',
    'phase3': '',
}

pid = str(os.getpid())
pidfile = "/tmp/ccPlot.pid"

if os.path.isfile(pidfile):
    print "%s already exists, exiting" % pidfile
    sys.exit()
else:
    file(pidfile, 'w').write(pid)

try:
    database = sqlite.connect('/opt/cc/power.sqlite')
    cursor = database.cursor()

    for value in values:
        cursor.execute(
            '''SELECT * FROM %s ORDER BY timestamp DESC LIMIT 2592000''' % value
        )
        values[value] = cursor.fetchall()

    cursor.close()
    database.close()

except Exception, e:
    print "Failed to access database"
    print "Exception:\n%s" % str(e)
    os.unlink(pidfile)
    sys.exit(e)

try:
    for value in values:
        for row in reversed(values[value]):
            utcTime  = time.gmtime(row[0])
            isoTime  = time.strftime('%Y-%m-%dT%H:%M:%SZ', utcTime)

            if points[value] == '':
                points[value] = [[row[0]], [row[1]], [isoTime], ]
            else:
                points[value][0].append(row[0])
                points[value][1].append(row[1])
                points[value][2].append(isoTime)

        try:
            figure = plt.figure()
            axis = figure.add_subplot(111)
            axis.set_xlabel('Date / Time')
            axis.set_ylabel('Power (W)')

            axis.plot(points[value][0], points[value][1])
#    axis.set_xticklabels(points[value][2])
#    plt.setp(axis.get_xticklabels(), rotation='60')

#    figure.subplots_adjust(bottom=0.34)

            figure.savefig('%s.png' % value)
            print "Written %s.png" % value

        except Exception, e:
            print "Failed to create graph"
            print "Exception:\n%s" % str(e)
            os.unlink(pidfile)
            sys.exit(e)

except Exception, e:
    print "Failed to create points for graph"
    print "Exception:\n%s" % str(e)
    os.unlink(pidfile)
    sys.exit(e)

os.unlink(pidfile)
