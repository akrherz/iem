"""Clean up some tables that contain bloaty NWS Text Data

called from RUN_2AM.sh
"""

from pyiem.database import get_dbconn
from pyiem.reference import state_names
from pyiem.util import logger

LOG = logger()

# reflect changes to docs/datasets/afos.md
PIL3_IGNORE = (
    "RR1 RR2 RR3 RR4 RR5 RR6 RR7 RR8 RR9 RRA RRS RRZ ECM ECS ECX LAV "
    "LEV MAV MET MTR MEX NBE NBH NBP NBS NBX OSO RSD RWR STO HML WRK "
    "SCV LLL GSM"
).split()
PIL_IGNORE = (
    "HPTNCF WTSNCF TSTNCF HD3RSA XF03DY XOBUS ECMNC1 SYNBOU MISWTM MISWTX "
    "MISMA1 MISAM1 XF07DY"
).split()
for abbr in state_names:
    # SCNWSH, le sigh
    PIL_IGNORE.append(f"SCN{abbr}")


def main():
    """Clean AFOS and friends"""
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor()

    acursor.execute(
        """
        delete from products WHERE
        entered < ('YESTERDAY'::date - '7 days'::interval) and
        entered > ('YESTERDAY'::date - '31 days'::interval) and
        (substr(pil, 1, 3) = ANY(%s) or pil = ANY(%s))
        """,
        (PIL3_IGNORE, PIL_IGNORE),
    )
    LOG.info("deleted %s rows", acursor.rowcount)
    if acursor.rowcount == 0:
        LOG.warning("Found no products to delete between 7-31 days")
    acursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
