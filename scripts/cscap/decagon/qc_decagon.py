import psycopg2


def get_entries():
    """Return a list of entries for usage"""
    cursor = pgconn.cursor()
    cursor.execute("""SELECT distinct uniqueid, plotid from decagon_data
    ORDER by uniqueid, plotid""")
    entries = []
    for row in cursor:
        entries.append([row[0], row[1]])
    return entries


def bounds_check():
    """ Values need to be physical! """
    cursor = pgconn.cursor()
    entries = get_entries()
    for (uniqueid, plotid) in entries:
        for v in range(1, 6):
            for n, lbound, ubound in zip(['moisture', 'temp', 'ec'],
                                         [0, -50, -0.01],
                                         [1, 50, 28]):
                if v > 1 and n == 'ec':
                    continue
                vname = "d%s%s_qc" % (v, n)
                vflag = "d%s%s_flag" % (v, n)
                cursor.execute("""
                    UPDATE decagon_data
                    SET """+vname+""" = null, """+vflag+""" = 'M'
                    where uniqueid = %s and plotid = %s and
                    ("""+vname+""" <= %s or """+vname+""" >= %s)
                """, (uniqueid, plotid, lbound, ubound))
                print(('Site: %s Plotid: %s Var: %-13s Hits: %s'
                       ) % (uniqueid, plotid, vname, cursor.rowcount))
                # for row in cursor:
                #    print vname, row[0].strftime("%Y%m%d%H%M"), row[1]


def ticker_temp():
    """ QC any values that tick too quickly over some period of time"""
    cursor = pgconn.cursor()
    entries = get_entries()
    n = 'temp'
    threshold = 10
    for (uniqueid, plotid) in entries:
        cursor2 = pgconn.cursor()
        for v in range(1, 6):
            vname = "d%s%s_qc" % (v, n)
            vflag = "d%s%s_flag" % (v, n)
            cursor.execute("""WITH data as(
            SELECT lag(valid) OVER (ORDER by valid ASC) as lag_valid,
            valid, lead(valid) OVER (ORDER by valid ASC) as lead_valid,
            lag("""+vname+""") OVER (ORDER by valid ASC) as lag_var,
            """ + vname + """ as var,
            lead("""+vname+""") OVER (ORDER by valid ASC) as lead_var
            from decagon_data
            WHERE uniqueid = %s and plotid = %s and """+vname+""" is not null)
            select lag_valid, valid, lead_valid, lag_var, var, lead_var
            from data WHERE abs(var - lag_var) > %s and
            (valid - lag_valid) < '2 hours'::interval ORDER by valid
            """, (uniqueid, plotid, threshold))
            print(('Site: %s Plotid: %s Var: %-11s Hits: %s'
                   ) % (uniqueid, plotid, vname, cursor.rowcount))
            for row in cursor:
                print(("valid: %s %s went from %s to %s at %s"
                       ) % (row[0].strftime("%Y%m%d %H%M"), vname,
                            row[3], row[4], row[1].strftime("%Y%m%d %H%M"))
                      )
                cursor2.execute("""UPDATE decagon_data SET
                """ + vname + """ = null, """ + vflag + """ = 'T'
                WHERE uniqueid = %s and plotid = %s and valid = %s
                """, (uniqueid, plotid, row[1]))
        cursor2.close()
        pgconn.commit()


def replace999():
    """ Simple replacement of -999 values with nulls """
    for v in range(1, 6):
        for n in ['moisture', 'temp', 'ec']:
            if v > 1 and n == 'ec':
                continue
            cursor = pgconn.cursor()
            cursor.execute("""UPDATE decagon_data SET
            d%s%s_flag = 'M', d%s%s = null, d%s%s_qc = null WHERE d%s%s = -999
            """ % (v, n, v, n, v, n, v, n))
            print "%s rows with -999 set to null for d%s%s" % (cursor.rowcount,
                                                               v, n)
            cursor.close()
            pgconn.commit()


if __name__ == '__main__':
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')

    replace999()
    # ticker_temp()
    # bounds_check()
