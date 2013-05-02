#!/bin/env python26

import httplib
import os
import signal
import sqlite3
import sys
import time
import urllib

values = {
    'temperature': [],
    'power': [],
#    'phase2': [],
#    'phase3': [],
}

csvs = {
    'temperature': '',
    'power': '',
#    'phase2': '',
#    'phase3': '',
}

pid = str(os.getpid())
pidfile = "/tmp/ccUploader.pid"

if os.path.isfile(pidfile):
    ##  print "%s already exists, exiting" % pidfile
    sys.exit()
else:
    file(pidfile, 'w').write(pid)

try:
    database = sqlite3.connect('/opt/cc/power.sqlite')
    cursor = database.cursor()

    for value in values:
        cursor.execute(
            '''SELECT * FROM %s WHERE uploaded = 0 ORDER BY timestamp DESC LIMIT 480''' % value
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
        for row in values[value]:
            utcTime  = time.gmtime(row[0])
            isoTime  = time.strftime('%Y-%m-%dT%H:%M:%SZ', utcTime)

            if csvs[value] == '':
                csvs[value] = "%s,%s" % (isoTime, row[1])
            else:
                csvs[value] = "%s\n%s,%s" % (csvs[value], isoTime, row[1])

except Exception, e:
    print "Failed to create CSV"
    print "Exception:\n%s" % str(e)
    os.unlink(pidfile)
    sys.exit(e)

headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain",
    #"Accept": "*/*",
    "X-PachubeApiKey": "-qALpnF43LScUy4BCmKDRsI59S545xIN56T8YvtMmCI",
}

for value in values:
    try:
        conn = httplib.HTTPConnection('api.pachube.com:80')
        conn.request(
            'POST',
            "/v2/feeds/40684/datastreams/%s/datapoints" % value,
            csvs[value],
            headers,
        )

        response = conn.getresponse()
        resp_str = response.read()

        conn.close()

        if int(response.status) == 200:
            try:
                database = sqlite3.connect('/opt/cc/power.sqlite')
                cursor = database.cursor()

                for row in values[value]:
                    cursor.execute(
                        '''UPDATE %s SET uploaded = 1 WHERE timestamp=?''' % value,
                        (row[0],)
                    )

                database.commit()
                cursor.close()
                database.close()

            except Exception, e:
                print "Failed to update database"
                print "Exception:\n%s" % str(e)
                continue

        else:
            pass
            # print "Failed to HTTP POST"
            # print "Response: %s %s\n%s" % (response.status, response.reason, resp_str,)


    except Exception, e:
        print "Failed to HTTP POST"
        print "Exception:\n%s" % str(e)
        continue

os.unlink(pidfile)
