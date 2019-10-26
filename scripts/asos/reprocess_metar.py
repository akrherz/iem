"""
 Reprocess RAW METAR data stored in the database, so to include more fields
"""
from __future__ import print_function
import datetime

from metar.Metar import Metar
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    icursor = pgconn.cursor()
    icursor2 = pgconn.cursor()

    sts = utc(2011, 8, 1)
    ets = utc(2011, 12, 1)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        icursor.execute(
            """
      select valid, station, metar from t"""
            + str(now.year)
            + """
      where metar is not null and valid >= %s and valid < %s
      and wxcodes is null
        """,
            (now, now + interval),
        )
        total = 0
        for row in icursor:
            try:
                mtr = Metar(row[2], row[0].month, row[0].year)
            except Exception:
                continue
            sql = "update t%s SET " % (now.year,)
            if mtr.max_temp_6hr:
                sql += "max_tmpf_6hr = %s," % (mtr.max_temp_6hr.value("F"),)
            if mtr.min_temp_6hr:
                sql += "min_tmpf_6hr = %s," % (mtr.min_temp_6hr.value("F"),)
            if mtr.max_temp_24hr:
                sql += "max_tmpf_24hr = %s," % (mtr.max_temp_24hr.value("F"),)
            if mtr.min_temp_24hr:
                sql += "min_tmpf_24hr = %s," % (mtr.min_temp_24hr.value("F"),)
            if mtr.precip_3hr:
                sql += "p03i = %s," % (mtr.precip_3hr.value("IN"),)
            if mtr.precip_6hr:
                sql += "p06i = %s," % (mtr.precip_6hr.value("IN"),)
            if mtr.precip_24hr:
                sql += "p24i = %s," % (mtr.precip_24hr.value("IN"),)
            if mtr.press_sea_level:
                sql += "mslp = %s," % (mtr.press_sea_level.value("MB"),)
            if mtr.weather:
                pwx = []
                for x in mtr.weather:
                    pwx.append(("").join([a for a in x if a is not None]))
                sql += "wxcodes = '{%s}'," % (",".join(pwx),)
            if sql == "update t%s SET " % (now.year,):
                continue
            sql = "%s WHERE station = '%s' and valid = '%s'" % (
                sql[:-1],
                row[1],
                row[0],
            )
            # print(sql)
            icursor2.execute(sql)
            total += 1
            if total % 1000 == 0:
                print("Done total: %s now: %s" % (total, now))
                pgconn.commit()
        now += interval
    icursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
