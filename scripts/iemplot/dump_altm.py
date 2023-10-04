"""Dumping altimeter data so that GEMPAK can analyze it."""
import datetime

import pandas as pd
from metpy.units import units
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go"""
    ts = datetime.datetime.utcnow().strftime("%y%m%d/%H00")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            SELECT t.id, alti from current c JOIN stations t on
            (t.iemid = c.iemid)
            WHERE alti > 0 and valid > (now() - '60 minutes'::interval)
            and t.state in ('IA','MO','IL','WI','IN','OH','KY','MI','SD','ND',
            'NE', 'KS') and network ~* 'ASOS'
        """,
            conn,
            index_col="id",
        )
    df["altm"] = (df["alti"].values * units("inHg")).to(units("hPa")).m

    with open("/mesonet/data/iemplot/altm.txt", "w") as fh:
        fh.write((" PARM = ALTM\n\n" "    STN    YYMMDD/HHMM      ALTM\n"))

        for sid, row in df.iterrows():
            fh.write("   %4s    %s  %8.2f\n" % (sid, ts, row["altm"]))


if __name__ == "__main__":
    main()
