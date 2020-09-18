"""Clean up some tables that contain bloaty NWS Text Data

called from RUN_2AM.sh
"""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Clean AFOS and friends"""
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor()

    # reflect changes to docs/datasets/afos.md
    acursor.execute(
        "delete from products WHERE "
        "entered < ('YESTERDAY'::date - '7 days'::interval) and "
        "entered > ('YESTERDAY'::date - '31 days'::interval) and "
        "(pil ~* '^(RR[1-9RSMAZ]|ECM|ECS|ECX|LAV|LEV|MAV|MET|MTR|MEX|NBE|"
        "NBH|NBP|NBS|NBX|RWR|STO|HML|WRK|OSO|SCV)' "
        "or pil in ('HPTNCF', 'WTSNCF','WRKTTU','TSTNCF', 'HD3RSA', "
        "'XF03DY', 'XOBUS', 'ECMNC1', 'SYNBOU', 'MISWTM', 'MISWTX', "
        "'MISMA1', 'MISAM1'))"
    )
    if acursor.rowcount == 0:
        LOG.info("Found no products to delete between 7-31 days")
    acursor.close()
    pgconn.commit()

    # Clean Postgis
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute("DELETE from text_products where geom is null")
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
