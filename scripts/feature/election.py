import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
icursor = COOP.cursor()

[R, D] = range(2)
years = numpy.arange(1900,2012,4)
us_results   = [R, R, R, D, D, R, R, R, D, D, D, D, D, R, R, D, D, R, R, D, R, R, R, D, D, R, R, D]
iowa_results = [R, R, R, D, R, R, R, R, D, D, R, R, D, R, R, R, D, R, R, R, R, R, D, D, D, D, R, D] # 72-

def runner(a, b):
    icursor.execute("""    
    SELECT avg(p) from (Select year, avg((high+low)/2.) as p from alldata_ia
    where station = 'IA0000' and month = %s GROUP by year) as foo
    """ % (a, ))
    row = icursor.fetchone()
    avg = row[0]
    avg = b
    #    Above  Below
    # D
    # R
    ia_table = numpy.zeros( (2,2), 'f')
    us_table = numpy.zeros( (2,2), 'f')
    for year in years:
        idx = (year - years[0]) / 4
        icursor.execute("""SELECT high from alldata_ia where
        station = 'IA0000' and year = %s and extract(doy from day) = %s""" % (year, a))
        row = icursor.fetchone()
        if row[0] > avg and iowa_results[ idx ] == D:
            ia_table[0,0] += 1
        elif row[0] <= avg and iowa_results[ idx ] == D:
            ia_table[0,1] += 1
        elif row[0] > avg and iowa_results[ idx ] == R:
            ia_table[1,0] += 1
        elif row[0] <= avg and iowa_results[ idx ] == R:
            ia_table[1,1] += 1
        
        if row[0] > avg and us_results[ idx ] == D:
            us_table[0,0] += 1
        elif row[0] <= avg and us_results[ idx ] == D:
            us_table[0,1] += 1
        elif row[0] > avg and us_results[ idx ] == R:
            us_table[1,0] += 1
        elif row[0] <= avg and us_results[ idx ] == R:
            us_table[1,1] += 1
            
    printer = False
    if (ia_table[0,0] + ia_table[1,1]) > 23:
        printer = True
    if (ia_table[1,0] + ia_table[0,1]) > 23:
        printer = True
    if (us_table[0,0] + us_table[1,1]) > 23:
        printer = True
    if (us_table[1,0] + us_table[0,1]) > 23:
        printer = True
    if not printer:
        return
    #if numpy.min(us_table) > 3 and numpy.min(ia_table) > 3:
    #    return
    print "_____________ %s %s ____________________" % (a, b)
    print "IA  ABOVE  BELOW    US   ABOVE  BELOW"
    print "D   %5.0f  %5.0f    D   %5.0f %5.0f" % (ia_table[0,0], ia_table[0,1],
                                           us_table[0,0], us_table[0,1])
    print "R   %5.0f  %5.0f    R   %5.0f %5.0f" % (ia_table[1,0], ia_table[1,1],
                                           us_table[1,0], us_table[1,1])
    
for i in range(68,365):
    for t in range(40,100, 10):
        runner(i, t)