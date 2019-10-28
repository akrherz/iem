"""Properly zap a period of data from the database"""
import sys
import subprocess
import datetime

from pyiem.util import get_dbconn


def do_isuag(nwsli, sts, ets):
    """Do ISUAG Table"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    # Cull 15minute
    cursor.execute(
        """
        UPDATE sm_15minute SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        rh_qc = null, rh_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts, ets),
    )
    print("    sm_15minute updated %s rows" % (cursor.rowcount,))
    # Cull hourly
    cursor.execute(
        """
        UPDATE sm_hourly SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        rh_qc = null, rh_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts, ets),
    )
    print("    sm_hourly updated %s rows" % (cursor.rowcount,))
    # cull daily
    cursor.execute(
        """
        UPDATE sm_daily SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        tair_c_min_qc = null, tair_c_min_f = 'M',
        tair_c_max_qc = null, tair_c_max_f = 'M',
        rh_avg_qc = null, rh_avg_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts.date(), ets.date()),
    )
    print("    sm_daily updated %s rows" % (cursor.rowcount,))
    cursor.close()
    pgconn.commit()
    pgconn.close()


def do_iem(nwsli, sts, ets):
    """Update the summary table"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    # cull iemre daily
    cursor.execute(
        """
        UPDATE summary s SET
        max_tmpf = null, min_tmpf = null, max_dwpf = null, min_dwpf = null,
        avg_rh = null, min_rh = null, max_rh = null
        FROM stations t
        WHERE t.id = %s and t.network = 'ISUSM' and s.iemid = t.iemid
        and day >= %s and day <= %s
    """,
        (nwsli, sts.date(), ets.date()),
    )
    print("    summary updated %s rows" % (cursor.rowcount,))
    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Go Main Go"""
    nwsli = argv[1]
    sts = datetime.datetime(
        int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])
    )
    ets = datetime.datetime(
        int(argv[6]), int(argv[7]), int(argv[8]), int(argv[9])
    )
    res = input("%s %s->%s, OK? y/[n] " % (nwsli, sts, ets))
    if str(res) != "y":
        print("ABORT")
        return
    do_iem(nwsli, sts, ets)
    do_isuag(nwsli, sts, ets)
    print("Redoing estimates")
    subprocess.call(["python", "fix_temps.py"])


if __name__ == "__main__":
    main(sys.argv)
