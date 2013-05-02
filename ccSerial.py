#!/bin/env python26

import calendar
import os
import serial
import signal
import sqlite3
import sys
import time
import xml.dom.minidom

sPort = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=57600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=10
)

##
##  <msg><src>CC128-v1.31</src><dsb>00338</dsb><time>11:04:53</time><tmpr>23.2</tmpr><sensor>0</sensor><id>00077</id><type>1</type><ch1><watts>00132</watts></ch1><ch2><watts>00000</watts></ch2><ch3><watts>00252</watts></ch3></msg>
##

while True:
    values = {}
    print ""

    try:
        line = sPort.readline()
	line = line[line.index('<'):line.rindex('>') + 1]

        dom = xml.dom.minidom.parseString(line)

        tmpr = dom.getElementsByTagName("tmpr")
        ch1  = dom.getElementsByTagName("ch1")
        ch2  = dom.getElementsByTagName("ch2")
        ch3  = dom.getElementsByTagName("ch3")

        values['temperature']  = tmpr[0].childNodes[0].nodeValue
        values['phase1'] = ch1[0].getElementsByTagName("watts")[0].childNodes[0].nodeValue
        values['phase2'] = ch2[0].getElementsByTagName("watts")[0].childNodes[0].nodeValue
        values['phase3'] = ch3[0].getElementsByTagName("watts")[0].childNodes[0].nodeValue

        utcTime  = time.gmtime()
        unixTime = calendar.timegm(utcTime)
        isoTime  = time.strftime('%Y-%m-%dT%H:%M:%SZ', utcTime)

        print "Currently: time=%s, temperature=%.1f, ch1=%d, ch2=%d, ch3=%d" % (
            isoTime,
            float(values['temperature']),
            int(values['phase1']),
            int(values['phase2']),
            int(values['phase3']),
        )

    except KeyboardInterrupt, e:
        sys.stderr.write('Interrupt\n')
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGINT)

    except SystemExit, e:
        sys.exit(e)

    except Exception, e:
        print "Did not parse:\n%s" % line
        print "Exception:\n%s" % str(e)
        continue

    try:
        database = sqlite3.connect('/opt/cc/power.sqlite')
        cursor = database.cursor()

        for value in values:
            cursor.execute('''INSERT INTO %s
                VALUES (?, ?, ?)''' % value, (int(unixTime), float(values[value]), int(0),))

            database.commit()

        cursor.close()
        database.close()

        print " -- Inserted into database"

    except KeyboardInterrupt, e:
        sys.stderr.write('Interrupt\n')
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGINT)

    except SystemExit, e:
        sys.exit(e)

    except Exception, e:
        print "Failed to insert into database:\n%s" % str(e)
        continue
