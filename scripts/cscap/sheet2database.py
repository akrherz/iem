"""A direct copy of a Google Spreadsheet to a postgresql database"""
import psycopg2
import pyiem.cscap_utils as util

config = util.get_config()
pgconn = psycopg2.connect(database='sustainablecorn',
                          host=config['database']['host'])
spr_client = util.get_spreadsheet_client(config)

JOB_LISTING = [
    ["15AjRh7dvwleWqJviz53JqQm8wxNru4bsgn16Ad_MtUU", 'xref_rotation'],
    ]


def do(spreadkey, tablename):
    """Process"""
    cursor = pgconn.cursor()
    cursor.execute("""DROP TABLE IF EXISTS %s""" % (tablename, ))
    listfeed = spr_client.get_list_feed(spreadkey, 'od6')
    for i, entry in enumerate(listfeed.entry):
        row = entry.to_dict()
        if i == 0:
            # Create the table
            sql = "CREATE TABLE %s (" % (tablename, )
            for key in row.keys():
                sql += "%s varchar," % (key, )
            sql = sql[:-1] + ")"
            cursor.execute(sql)
            cursor.execute("""
            GRANT SELECT on %s to nobody,apache
            """ % (tablename, ))
        values = []
        cols = []
        for key in row.keys():
            cols.append(key)
            values.append(row[key].strip())
        sql = "INSERT into %s (%s) VALUES (%s)" % (tablename, ",".join(cols),
                                                   ",".join(["%s"]*len(cols)))
        cursor.execute(sql, values)
    cursor.close()
    pgconn.commit()


def main():
    """Do Something"""
    for (spreadkey, tablename) in JOB_LISTING:
        do(spreadkey, tablename)

if __name__ == '__main__':
    main()
