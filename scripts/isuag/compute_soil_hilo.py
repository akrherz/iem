"""
Compute Soil High and Low Temperatures for any missing values!
"""
import iemdb
ISUAG = iemdb.connect('isuag', bypass=True)
icursor = ISUAG.cursor()


if __name__ == '__main__':
    icursor = ISUAG.cursor()
    icursor2 = ISUAG.cursor()
    icursor.execute("""SELECT station, valid from daily WHERE c30h is null""")
    for row in icursor:
        icursor2.execute("""SELECT max(c300), min(c300) from hourly WHERE
        valid >= '%s 00:00' and valid < '%s 23:59' and station = '%s'""" % (
            row[1].strftime("%Y-%m-%d"), row[1].strftime("%Y-%m-%d"),
            row[0]))
        row2 = icursor2.fetchone()
        icursor2.execute("""UPDATE daily SET
        c30l = %s, c30h = %s WHERE station = %s and valid = %s""",
        (row2[1], row2[0], row[0], row[1]))
        
    ISUAG.commit()