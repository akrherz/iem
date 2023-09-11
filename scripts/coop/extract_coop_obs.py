""" Dump out obs from the database for use by other apps """
import datetime
import os
import subprocess
import zipfile

import shapefile
from pyiem.util import get_dbconnc


def main():
    """Go main!"""
    pgconn, icursor = get_dbconnc("iem")

    now = datetime.datetime.now()
    ts = now.strftime("%Y%m%d")
    yyyy = now.strftime("%Y")

    cob = {}

    icursor.execute(
        f"""SELECT s.id, coalesce(c.pday, 0) as pday,
        coalesce(c.snow,-99) as snow, coalesce(c.snowd,-99) as snowd,
        coalesce(c.max_tmpf, -99) as max_tmpf,
        coalesce(c.min_tmpf, -99) as min_tmpf,
        ST_x(s.geom) as lon, ST_y(s.geom) as lat, s.name,
        c2.valid at time zone 'UTC' as vvv, s.elevation
        from summary_{yyyy} c, current c2, stations s WHERE
        c.iemid = c2.iemid and s.iemid = c.iemid and
        s.network ~* 'COOP' and min_tmpf > -99 and c2.valid > 'TODAY'
        and day = 'TODAY'"""
    )

    for row in icursor:
        thisStation = row["id"]
        cob[thisStation] = {}
        thisPrec = row["pday"]
        thisSnow = row["snow"]
        thisSnowD = row["snowd"]
        thisHigh = row["max_tmpf"]
        thisLow = row["min_tmpf"]

        # First we update our cobs dictionary
        cob[thisStation]["TMPX"] = int(thisHigh)
        cob[thisStation]["TMPN"] = int(thisLow)
        cob[thisStation]["P24I"] = round(float(thisPrec), 2)
        cob[thisStation]["SNOW"] = float(thisSnow)
        cob[thisStation]["SNOD"] = float(thisSnowD)
        cob[thisStation]["LAT"] = row["lat"]
        cob[thisStation]["LON"] = row["lon"]
        cob[thisStation]["NAME"] = row["name"]
        cob[thisStation]["ELEV_M"] = row["elevation"]
        cob[thisStation]["PMOI"] = 0.0
        cob[thisStation]["SMOI"] = 0.0
        cob[thisStation]["HHMM"] = row["vvv"].strftime("%H%M")

    icursor.execute(
        f"""
        SELECT t.id, sum(pday) as tprec,
        sum( case when snow > 0 THEN snow ELSE 0 END) as tsnow
        from summary_{now.year} s, stations t WHERE
        date_part('month', day) = date_part('month', CURRENT_TIMESTAMP::date)
        and date_part('year', day) = {now.year}
        and pday >= 0.00 and t.network ~* 'COOP' and t.iemid = s.iemid
        GROUP by id
        """
    )

    for row in icursor:
        thisStation = row["id"]
        thisPrec = row["tprec"]
        thisSnow = row["tsnow"]
        if thisStation not in cob:
            continue
        cob[thisStation]["PMOI"] = round(float(thisPrec), 2)
        cob[thisStation]["SMOI"] = round(float(thisSnow), 2)
    pgconn.close()
    with open("coop.csv", "w", encoding="ascii") as csv:
        csv.write(
            (
                "nwsli,site_name,longitude,latitude,date,time,high_f,low_f,"
                "prec_in,snow_in,snow_depth_in,prec_mon_in,snow_mon_in,"
                "elevation_m\n"
            )
        )

        w = shapefile.Writer(f"coop_{ts}")
        w.field("SID", "C", 5, 0)
        w.field("SITE_NAME", "C", 64, 0)
        w.field("ELEV_M", "F", 10, 2)
        w.field("YYYYMMDD", "C", 8, 0)
        w.field("HHMM", "C", 4, 0)
        w.field("HI_T_F", "N", 10, 0)
        w.field("LO_T_F", "N", 10, 0)
        w.field("PREC", "F", 10, 2)
        w.field("SNOW", "F", 10, 2)
        w.field("SDEPTH", "F", 10, 2)
        w.field("PMONTH", "F", 10, 2)
        w.field("SMONTH", "F", 10, 2)
        for sid, item in cob.items():
            w.point(item["LON"], item["LAT"])
            if item["P24I"] < 0:
                item["P24I"] = -99.0
            if item["SNOW"] < 0:
                item["SNOW"] = -99.0
            if item["SNOD"] < 0:
                item["SNOD"] = -99.0
            if item["PMOI"] < 0:
                item["PMOI"] = -99.0
            if item["SMOI"] < 0:
                item["SMOI"] = -99.0
            w.record(
                sid,
                item["NAME"],
                item["ELEV_M"],
                ts,
                "1200",
                item["TMPX"],
                item["TMPN"],
                item["P24I"],
                item["SNOW"],
                item["SNOD"],
                item["PMOI"],
                item["SMOI"],
            )

            csv.write(
                f"{sid},{item['NAME'].replace(',', ' ')},{item['LON']:.4f},"
                f"{item['LAT']:.4f},{ts},{item['HHMM']},{item['TMPX']},"
                f"{item['TMPN']},{item['P24I']},{item['SNOW']},{item['SNOD']},"
                f"{item['PMOI']},{item['SMOI']},{item['ELEV_M']:.1f}\n"
            )

        w.close()

    pqstr = f"plot c {now:%Y%m%d%H%M} csv/coop.csv bogus csv"
    subprocess.call(["pqinsert", "-p", pqstr, "coop.csv"])
    os.unlink("coop.csv")

    with zipfile.ZipFile(f"coop_{ts}.zip", "w") as zfn:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zfn.writestr(f"coop_{ts}.prj", fh.read())
        with open("data.desc", encoding="ascii") as fh:
            zfn.writestr(f"coop_{ts}.txt", fh.read())
        for suffix in ["shp", "shx", "dbf"]:
            zfn.write(f"coop_{ts}.{suffix}")

    cmd = [
        "pqinsert",
        "-p",
        (
            f"zip ac {now:%Y%m%d%H%M} gis/shape/4326/iem/coopobs.zip "
            f"GIS/coop_{ts}.zip zip"
        ),
        f"coop_{ts}.zip",
    ]
    subprocess.call(cmd)
    for suffix in ["shp", "shx", "dbf", "zip"]:
        os.unlink(f"coop_{ts}.{suffix}")


if __name__ == "__main__":
    main()
