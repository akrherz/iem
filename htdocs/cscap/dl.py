#!/usr/bin/python
"""

"""
import sys
import psycopg2
import psycopg2.extras
import ConfigParser
import cgi

config = ConfigParser.ConfigParser()
config.read('/mesonet/www/apps/iemwebsite/scripts/cscap/mytokens.cfg')

def clean( val ):
    ''' Clean the value we get '''
    if val is None:
        return ''
    if val.strip().lower() == 'did not collect':
        return 'DNC'
    if val.strip().lower() == 'n/a':
        return 'NA'
    return val

def check_auth(form):
    ''' Make sure request is authorized '''
    if form.getfirst('hash') != config.get('appauth', 'sharedkey'):
        sys.exit()
    
def get_nitratedata():
    ''' Fetch some nitrate data, for now '''
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb',
                              user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    res = "uniqueid,plotid,year,depth,soil15,soil16,soil23\n"
    cursor.execute("""SELECT site, plotid, depth, varname, year, value
    from soil_nitrate_data WHERE value is not null
    and value ~* '[0-9\.]' and value != '.' and value !~* '<'
    and site in ('MASON', 'KELLOGG', 'GILMORE', 'ISUAG', 'WOOSTER.COV',
    'SEPAC', 'BRADFORD.C', 'BRADFORD.B1', 'BRADFORD.B2', 'FREEMAN')""")
    data = {}
    for row in cursor:
        key = "%s|%s|%s|%s" % (row['site'], row['plotid'], row['year'],
                                row['depth'])
        if not data.has_key(key):
            data[key] = {}
        data[key][row['varname']] = clean(row["value"])

    for key in data.keys():
        tokens = key.split("|")
        res += "%s,%s,%s,%s,%s,%s,%s\n" % (tokens[0], tokens[1],
                tokens[2], tokens[3],
                data[key].get('SOIL15', ''), data[key].get('SOIL16', ''),
                data[key].get('SOIL23', ''))
    return res

def get_agdata():
    """
    Go to Google and demand my data back!
    """
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb',
                              user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""SELECT site, a.plotid, year, varname, value,
    p.rep, p.tillage, p.rotation , p.nitrogen
    from agronomic_data a JOIN plotids p on (p.uniqueid = a.site and
    p.plotid = a.plotid) where 
    varname in ('AGR1', 'AGR2', 'AGR7', 'AGR15', 'AGR16', 'AGR17', 'AGR19')
    and value ~* '[0-9\.]' and value != '.' and value !~* '<'
    and (site in ('MASON', 'KELLOGG', 'GILMORE', 'ISUAG', 'WOOSTER.COV',
    'SEPAC', 'FREEMAN') or
    (site in ('BRADFORD.C', 'BRADFORD.B1', 'BRADFORD.B2') and p.nitrogen = 'NIT3')
    )""")
    data = {}
    for row in cursor:
        key = "%s|%s|%s|%s|%s|%s|%s" % (row['site'], row['plotid'], row['year'],
                                row['rep'], row['tillage'], row['rotation'],
                                row['nitrogen'])
        if not data.has_key(key):
            data[key] = {}
        data[key][row['varname']] = clean(row["value"])

    # Get the Soil Nitrate data we are going to join with
    cursor.execute("""
    SELECT site, plotid, depth, varname, year, avg(value::float)
    from soil_nitrate_data WHERE value is not null
    and value ~* '[0-9\.]' and value != '.' and value !~* '<'
    and site in ('MASON', 'KELLOGG', 'GILMORE', 'ISUAG', 'WOOSTER.COV',
    'SEPAC', 'BRADFORD.C', 'BRADFORD.B1', 'BRADFORD.B2', 'FREEMAN') 
    and varname = 'SOIL23' GROUP by site, plotid, depth, varname, year
    """)
    sndata = {}
    for row in cursor:
        key = "%s|%s|%s|%s|%s" % (row['site'], row['plotid'], row['year'],
                               row['varname'], row['depth'])
        sndata[key] = row['avg']

    res = ("uniqueid,plotid,year,rep,tillage,rotation,nitrogen,agr1,agr2,agr7,"
          +"agr15,agr16,agr17,agr19,agr23_0-30,agr23_30-60,agr23_60-90,agr23_90-120\n")
    for key in data.keys():
        tokens = key.split("|")
        lkp = "%s|%s|%s|%s" % (tokens[0], tokens[1], tokens[2], 'SOIL23')
        res += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                tokens[0], tokens[1],
                tokens[2], tokens[3], tokens[4], tokens[5], tokens[6],
                data[key].get('AGR1', ''), data[key].get('AGR2', ''),
                data[key].get('AGR7', ''), data[key].get('AGR15', ''),
                data[key].get('AGR16', ''), data[key].get('AGR17', ''),
                data[key].get('AGR19', ''),
                sndata.get(lkp+"|0 - 30", 'M'),
                sndata.get(lkp+"|30 - 60", 'M'),
                sndata.get(lkp+"|60 - 90", 'M'),
                sndata.get(lkp+"|90 - 120", 'M')                
                )
    
    return res
    
if __name__ == '__main__':
    ''' See how we are called '''
    form = cgi.FieldStorage()
    sys.stdout.write("Content-type: text/plain\n\n")
    check_auth(form)
    report = form.getfirst('report', 'ag1')
    if report == 'ag1':
        sys.stdout.write( get_agdata() )
    else:
        sys.stdout.write( get_nitratedata() )
