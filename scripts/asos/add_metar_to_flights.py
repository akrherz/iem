""" Take a file of flight info and add METAR obs to it! """
import datetime
import psycopg2.extras
import pytz
from pyiem.util import get_dbconn
pgconn = get_dbconn('asos', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def get_data(sid, valid):
    """ Go get data for this time! """
    if sid[0] == 'K':
        sid = sid[1:]

    cursor.execute("""
        SELECT valid at time zone 'UTC' as utctime, *,
        case when presentwx is null then '' else presentwx end as pwx,
        case when metar is null then '' else metar end as metarwx
        from alldata WHERE valid BETWEEN %s and %s and station = %s
    """, (valid - datetime.timedelta(hours=2),
          valid + datetime.timedelta(hours=2), sid))

    before = {}
    after = {}
    before_delta = -7200
    after_delta = 7200
    for row in cursor:
        utc = row['utctime'].replace(tzinfo=pytz.timezone("UTC"))
        diff = (utc - valid).days * 86400 + (utc - valid).seconds
        # After
        if utc > valid:
            if diff < after_delta:
                after_delta = diff
                after = row.copy()
        # Before
        else:
            if diff > before_delta:
                before_delta = diff
                before = row.copy()

    return before, after


def timefmt(val):
    """ Nice formatter """
    if val is None:
        return "NULL"
    return val.strftime("%Y-%m-%d %H:%M:%S.000")


def format_entry(arr):
    """ Convert a dict into csv that we want """
    return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," % (
        arr.get('station', 'NULL'), timefmt(arr.get('utctime')),
        arr.get('tmpf'), arr.get('drct'), arr.get('sknt'), arr.get('gust'),
        arr.get('vsby'),
        arr.get('skyc1'), arr.get('skyc2'), arr.get('skyc3'), arr.get('skyc4'),
        arr.get('skyl1'), arr.get('skyl2'), arr.get('skyl3'), arr.get('skyl4'),
        arr.get('p01i'), arr.get('pwx', '').replace(',', ' '),
        arr.get('metarwx', 'NULL').replace("\n", " "))


def main():
    o = open('flight.csv', 'w')
    for linenum, line in enumerate(
                open('FlightsForMetar.csv').read().split("\r")):
        if linenum == 0:
            o.write((
                "%s,"
                "DepB_Metar_station,DepB_Metar_valid,DepB_tmpf,DepB_drct,DepB_sknt,DepB_gust,DepB_vsby,DepB_skyc1,DepB_skyc2,DepB_skyc3,DepB_skyc4,DepB_skyl1,DepB_skyl2,DepB_skyl3,DepB_skyl4,DepB_p01i,DepB_presentwx,DepB_Metar,"
                "DepA_Metar_station,DepA_Metar_valid,DepA_tmpf,DepA_drct,DepA_sknt,DepA_gust,DepA_vsby,DepA_skyc1,DepA_skyc2,DepA_skyc3,DepA_skyc4,DepA_skyl1,DepA_skyl2,DepA_skyl3,DepA_skyl4,DepA_p01i,DepA_presentwx,DepA_Metar,"
                "ArrB_Metar_station,ArrB_Metar_valid,ArrB_tmpf,ArrB_drct,ArrB_sknt,ArrB_gust,ArrB_vsby,ArrB_skyc1,ArrB_skyc2,ArrB_skyc3,ArrB_skyc4,ArrB_skyl1,ArrB_skyl2,ArrB_skyl3,ArrB_skyl4,ArrB_p01i,ArrB_presentwx,ArrB_Metar,"
                "ArrA_Metar_station,ArrA_Metar_valid,ArrA_tmpf,ArrA_drct,ArrA_sknt,ArrA_gust,ArrA_vsby,ArrA_skyc1,ArrA_skyc2,ArrA_skyc3,ArrA_skyc4,ArrA_skyl1,ArrA_skyl2,ArrA_skyl3,ArrA_skyl4,ArrA_p01i,ArrA_presentwx,ArrA_Metar,\n") % (line.strip(),))
            continue
        if linenum % 1000 == 0:
            print 'Processed %8s/%s lines...' % (linenum, 20683126)
        tokens = line.split(",")
        deptime = datetime.datetime.strptime(tokens[5][:19], '%Y-%m-%d %H:%M:%S')
        deptime = deptime.replace(tzinfo=pytz.timezone("UTC"))
        arrtime = datetime.datetime.strptime(tokens[7][:19], '%Y-%m-%d %H:%M:%S')
        arrtime = arrtime.replace(tzinfo=pytz.timezone("UTC"))
        depicao = tokens[4]
        arricao = tokens[6]

        arrdata_b, arrdata_a = get_data(arricao, arrtime)
        depdata_b, depdata_a = get_data(depicao, deptime)

        o.write("%s,%s%s%s%s\n" % (line.strip(),
                                   format_entry(depdata_b),
                                   format_entry(depdata_a),
                                   format_entry(arrdata_b),
                                   format_entry(arrdata_a),
                                   ))

    o.close()

if __name__ == '__main__':
    main()
