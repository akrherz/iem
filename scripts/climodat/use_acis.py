"""Use data provided by ACIS to replace climodat data"""
import requests
import sys
import psycopg2
import datetime

SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    if val in ['M', 'S']:
        return None
    if val == 'T':
        return 0.0001
    try:
        return float(val)
    except:
        print("failed to convert %s to float, using None" % (repr(val),))
        return None


def main(station, acis_station):
    table = "alldata_%s" % (station[:2],)
    payload = {"sid": acis_station,
               "sdate": "1850-01-01",
               "edate": "2017-01-01",
               "elems": "maxt,mint,pcpn,snow,snwd"}
    req = requests.post(SERVICE, json=payload)
    j = req.json()
    pgconn = psycopg2.connect(database='coop', host='localhost', port=5555,
                              user='mesonet')
    cursor = pgconn.cursor()
    for row in j['data']:
        date = row[0]
        (high, low, precip, snow, snowd) = map(safe, row[1:])
        if all([a is None for a in (high, low, precip, snow, snowd)]):
            continue
        cursor.execute("""
        UPDATE """ + table + """ SET high = %s, low = %s, precip = %s,
        snow = %s, snowd = %s WHERE station = %s and day = %s
        """, (high, low, precip, snow, snowd, station, date))
        if cursor.rowcount == 0:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            sday = "%02i%02i" % (date.month, date.day)
            print("Adding entry for %s" % (date,))
            cursor.execute("""INSERT into """ + table + """ (station, day,
            high, low, precip, snow, snowd, sday, year, month, estimated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'f')
            """, (station, date, high, low, precip, snow, snowd, sday,
                  date.year, date.month))
    cursor.close()
    pgconn.commit()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
