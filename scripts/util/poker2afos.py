"""Ingest the files kindly sent to me by poker"""
from __future__ import print_function
import glob
import re
import datetime
import subprocess
import os

import pytz
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.product import TextProduct

BAD_CHARS = r"[^\n\r\001\003a-zA-Z0-9:\(\)\%\.,\s\*\-\?\|/><&$=\+\@]"
DEBUG = False
PGCONN = get_dbconn("afos")
XREF_SOURCE = {
    "KDSM": "KDMX",
    "KOKC": "KOUN",
    "KALB": "KALY",
    "KATL": "KFFC",
    "KAUS": "KEWX",
    "KBHM": "KBMX",
    "KBIL": "KBYZ",
    "KBNA": "KOHX",
    "KBOS": "KBOX",
    "KDEN": "KBOU",
    "KDFW": "KFWD",
    "KDTW": "KDTX",
    "KEKO": "KLKN",
    "KELP": "KEPZ",
    "KEYW": "KKEY",
    "KFAT": "KHNX",
    "KFLG": "KFGZ",
    "KHOU": "KHGX",
    "KHSV": "KHUN",
    "KLAS": "KVEF",
    "KLAX": "KLOX",
    "KLBB": "KLUB",
    "KLIT": "KLZK",
    "KLSE": "KARX",
    "KMCI": "KEAX",
    "KMEM": "KMEG",
    "KMIA": "KMFL",
    "KMLI": "KDVN",
    "KMSP": "KMPX",
    "KNEW": "KLIX",
    "KNYC": "KOKX",
    "KOMA": "KOAX",
    "KORD": "KLOT",
    "KCHI": "KLOT",
    "KMMO": "KLOT",
    "KPDX": "KPQR",
    "KPHX": "KPSR",
    "KPIT": "KPBZ",
    "KRAP": "KUNR",
    "KRDU": "KRAH",
    "KSAC": "KSTO",
    "KSAN": "KSGX",
    "KSAT": "KEWX",
    "KSFO": "KSTO",
    "KSTL": "KLSX",
    "KTLH": "KTAE",
    "KTUL": "KTSA",
    "KTUS": "KTWC",
    "KALO": "KDMX",
    "KDBQ": "KDVN",
    "KCAK": "KCLE",
    "KHLN": "KTFX",
    "KPNS": "KMOB",
    "KAVP": "KBGM",
    "KCOS": "KPUB",
    "KERI": "KCLE",
    "KTPA": "KTBW",
    "KWMC": "KLKN",
    "KSYR": "KBGM",
    "KPBI": "KMFL",
    "KCPR": "KRIW",
    "KCLT": "KGSP",
    "KBFL": "KHNX",
    "KEUG": "KPQR",
    "KYNG": "KCLE",
    "KCSG": "KFFC",
    "KALS": "KPUB",
    "KBPT": "KLCH",
    "KDCA": "KLWX",
    "KLND": "KRIW",
    "KTOL": "KCLE",
    "KAHN": "KFFC",
    "KMFD": "KCLE",
    "KBFF": "KCYS",
    "KAST": "KPQR",
    "KORH": "KBOX",
    "KSPS": "KOUN",
    "KSMX": "KLOX",
    "KMKC": "KWNS",
    "KCRW": "KRLX",
    "KSDF": "KLMK",
    "KSEA": "KSEW",
    "KMKE": "KMKX",
    "KMSN": "KMKX",
    "KPHL": "KPHI",
    "KPWM": "KGYX",
    "KARB": "KDTX",
    "KFTW": "KFWD",
    "KFSM": "KLZK",
    "KLEX": "KLMK",
    "KEVV": "KPAH",
    "KACT": "KFWD",
}


def process(order):
    """ Process this timestamp """
    cursor = PGCONN.cursor()
    ts = datetime.datetime.strptime(order[:6], "%y%m%d").replace(
        tzinfo=pytz.utc
    )
    base = ts - datetime.timedelta(days=2)
    ceiling = ts + datetime.timedelta(days=2)
    subprocess.call("tar -xzf %s" % (order,), shell=True)
    inserts = 0
    deletes = 0
    filesparsed = 0
    bad = 0
    for fn in glob.glob("%s[0-2][0-9].*" % (order[:6],)):
        content = re.sub(
            BAD_CHARS, "", open(fn, "rb").read().decode("ascii", "ignore")
        )
        # Now we are getting closer, lets split by the delimter as we
        # may have multiple products in one file!
        for bulletin in content.split("\001"):
            if bulletin == "":
                continue
            try:
                bulletin = noaaport_text(bulletin)
                prod = TextProduct(bulletin, utcnow=ts, parse_segments=False)
                prod.source = XREF_SOURCE.get(prod.source, prod.source)
            except Exception as exp:
                if DEBUG:
                    o = open("/tmp/bad/%s.txt" % (bad,), "w")
                    o.write(bulletin)
                    o.close()
                    print("Parsing Failure %s" % (exp,))
                bad += 1
                continue
            if prod.valid < base or prod.valid > ceiling:
                # print('Timestamp out of bounds %s %s %s' % (base, prod.valid,
                #                                            ceiling))
                bad += 1
                continue

            table = "products_%s_%s" % (
                prod.valid.year,
                ("0712" if prod.valid.month > 6 else "0106"),
            )
            cursor.execute(
                """
                DELETE from """
                + table
                + """ WHERE pil = %s and
                entered = %s and source = %s and data = %s
            """,
                (prod.afos, prod.valid, prod.source, bulletin),
            )
            deletes += cursor.rowcount
            cursor.execute(
                """
                INSERT into """
                + table
                + """
                (data, pil, entered, source, wmo) values (%s,%s,%s,%s,%s)
            """,
                (bulletin, prod.afos, prod.valid, prod.source, prod.wmo),
            )
            inserts += 1

        os.unlink(fn)
        filesparsed += 1
    print(
        ("%s Files Parsed: %s Inserts: %s Deletes: %s Bad: %s")
        % (order, filesparsed, inserts, deletes, bad)
    )
    cursor.close()
    PGCONN.commit()
    # remove cruft
    for fn in glob.glob("*.wmo"):
        os.unlink(fn)
    os.rename(order, "a" + order)


def main():
    """ Go Main Go """
    os.chdir("/mesonet/tmp/poker")
    for order in glob.glob("??????.DDPLUS.tar.gz"):
        process(order)


if __name__ == "__main__":
    # do something
    main()
