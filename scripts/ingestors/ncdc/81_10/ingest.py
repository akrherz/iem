"""
  Process NCDC's 1981-2010 dataset into the IEM database for usage by
  all kinds of apps

  http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/station-inventories/temp-inventory.txt
  http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/station-inventories/prcp-inventory.txt
  http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/precipitation/ytd-prcp-normal.txt
  http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/temperature/dly-tmin-normal.txt
  http://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/products/temperature/dly-tmax-normal.txt

"""
import datetime

from pyiem.util import get_dbconn


def compute_stations():
    """ Logic to resolve, which stations we care about and add necessary
    station metadata about them! """
    stations = []
    pass1 = []
    for line in open("temp-inventory.txt"):
        pass1.append(line[:11])

    # Now we iterate over the precip inventory
    for line in open("prcp-inventory.txt"):
        if line[:11] not in pass1:
            continue
        # We have a station we care about!
        stations.append(line[:11])
    return stations


def ingest(stations, pgconn):
    """ Ingest the data into the database! """

    data = {}

    print("Process PRCP")
    for line in open("ytd-prcp-normal.txt"):
        if line[:11] not in stations:
            continue
        tokens = line.split()
        dbid = tokens[0]
        if dbid not in data:
            data[dbid] = {}

        month = tokens[1]
        for t in range(2, len(tokens)):
            token = tokens[t]
            val = int(token[:-1]) / 100.0
            if val == "-8888":
                continue
            d = "2000-%s-%02i" % (month, t - 1)
            data[dbid][d] = {}
            data[dbid][d]["precip"] = val

    print("Process TMIN")
    for line in open("dly-tmin-normal.txt"):
        if line[:11] not in stations:
            continue
        tokens = line.split()
        dbid = tokens[0]

        month = tokens[1]
        for t in range(2, len(tokens)):
            token = tokens[t]
            val = int(token[:-1]) / 10.0
            if val == "-8888":
                continue
            d = "2000-%s-%02i" % (month, t - 1)
            data[dbid][d]["tmin"] = val

    print("Process TMAX")
    for line in open("dly-tmax-normal.txt"):
        if line[:11] not in stations:
            continue
        tokens = line.split()
        dbid = tokens[0]

        month = tokens[1]
        for t in range(2, len(tokens)):
            token = tokens[t]
            val = int(token[:-1]) / 10.0
            if val == "-8888":
                continue
            d = "2000-%s-%02i" % (month, t - 1)
            data[dbid][d]["tmax"] = val

    for dbid in data:
        ccursor = pgconn.cursor()
        now = datetime.datetime(2000, 1, 1)
        ets = datetime.datetime(2001, 1, 1)
        interval = datetime.timedelta(days=1)
        running = 0
        while now < ets:
            d = now.strftime("%Y-%m-%d")
            # Precip data is always missing on leap day, sigh
            if d == "2000-02-29":
                precip = 0
            else:
                precip = data[dbid][d]["precip"] - running
                running = data[dbid][d]["precip"]

            ccursor.execute(
                """
                INSERT into ncdc_climate81
                (station, valid, high, low, precip)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (
                    dbid,
                    d,
                    data[dbid][d]["tmax"],
                    data[dbid][d]["tmin"],
                    precip,
                ),
            )
            now += interval
        ccursor.close()
        pgconn.commit()


def main():
    """ Go main Go """
    pgconn = get_dbconn("coop")

    stations = compute_stations()
    ingest(stations, pgconn)


if __name__ == "__main__":
    # Go
    main()
