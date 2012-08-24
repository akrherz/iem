"""
 Our HADS database gets loaded up with duplicates, this cleans it up.
 
 called from RUN_MIDNIGHT.sh
"""
import mx.DateTime
import iemdb
HADS = iemdb.connect('hads')

def query(sql):
    """
    Do a query and make it atomic
    """
    hcursor = HADS.cursor()
    hcursor.execute("set work_mem='4GB'")
    hcursor.execute("SET TIME ZONE 'GMT'")
    hcursor.execute(sql)
    hcursor.close()
    HADS.commit()

def do(ts):
    # Delete schoolnet data, since we created it in the first place!
    sql = """DELETE from raw%s WHERE station IN 
              (SELECT id from stations WHERE network in ('KCCI','KELO','KIMT')
              )""" % (ts.strftime("%Y_%m"),)
    query(sql)
    
    # Extract unique obs to special table
    sql = """CREATE table tmp as select distinct * from raw%s WHERE valid BETWEEN 
           '%s' and '%s'""" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), 
           (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
    query(sql)
    
    # Delete them all!
    sql = """delete from raw%s WHERE valid BETWEEN 
           '%s' and '%s'""" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d"), 
           (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y-%m-%d"))
    query(sql)
    
    sql = "DROP index raw%s_idx" % (ts.strftime("%Y_%m"),)
    query(sql)
    sql = "DROP index raw%s_valid_idx" % (ts.strftime("%Y_%m"),)
    query(sql)
    
    # Insert from special table
    sql = "INSERT into raw%s SELECT * from tmp" % (ts.strftime("%Y_%m"),)
    query(sql)

    sql = "CREATE index raw%s_idx on raw%s(station,valid)" % (
                            ts.strftime("%Y_%m"), ts.strftime("%Y_%m"))
    query(sql)
    sql = "CREATE index raw%s_valid_idx on raw%s(valid)" % (
                            ts.strftime("%Y_%m"), ts.strftime("%Y_%m"))
    query(sql)

    sql = "DROP TABLE tmp"
    # drop special table!
    query(sql)

do( mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1) )

#sts = mx.DateTime.DateTime(2007,12,1)
#ets = mx.DateTime.DateTime(2008,1,1)
#interval = mx.DateTime.RelativeDateTime(days=1)
#now = sts
#while (now < ets):
#  do( now )
#  now += interval
