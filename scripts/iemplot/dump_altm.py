"""Dumping altimeter data so that GEMPAK can analyze it."""
import datetime

from pyiem.util import get_dbconnstr
from pandas import read_sql
from metpy.units import units


def main():
    """Go Main Go"""
    ts = datetime.datetime.utcnow().strftime("%y%m%d/%H00")

    df = read_sql(
        """
        SELECT t.id, alti from current c JOIN stations t on (t.iemid = c.iemid)
        WHERE alti > 0 and valid > (now() - '60 minutes'::interval)
        and t.state in ('IA','MO','IL','WI','IN','OH','KY','MI','SD','ND','NE',
        'KS') and network ~* 'ASOS'
     """,
        get_dbconnstr("iem"),
        index_col="id",
    )
    df["altm"] = (df["alti"].values * units("inHg")).to(units("hPa")).m

    with open("/mesonet/data/iemplot/altm.txt", "w") as fh:
        fh.write((" PARM = ALTM\n\n" "    STN    YYMMDD/HHMM      ALTM\n"))

        for sid, row in df.iterrows():
            fh.write("   %4s    %s  %8.2f\n" % (sid, ts, row["altm"]))


if __name__ == "__main__":
    main()
