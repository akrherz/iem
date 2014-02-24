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

def check_auth(form):
    ''' Make sure request is authorized '''
    if form.getfirst('hash') != config.get('appauth', 'sharedkey'):
        sys.exit()
    
def get_nitratedata():
    ''' Fetch some nitrate data, for now '''
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb',
                              user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    res = "plotid,depth,soil15,soil16,soil23\n"
    cursor.execute("""SELECT site, plotid, depth, varname, year, value
    from soil_nitrate_data WHERE value is not null""")
    data = {}
    for row in cursor:
        key = "%s|%s|%s|%s" % (row['site'], row['plotid'], row['year'],
                                row['depth'])
        if not data.has_key(key):
            data[key] = {}
        data[key][row['varname']] = row["value"]

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
    p.rep, p.tillage, p.rotation 
    from agronomic_data a JOIN plotids p on (p.uniqueid = a.site and
    p.plotid = a.plotid) where 
    varname in ('AGR1', 'AGR2', 'AGR7', 'AGR15', 'AGR16', 'AGR17', 'AGR19')""")
    data = {}
    for row in cursor:
        key = "%s|%s|%s|%s|%s|%s" % (row['site'], row['plotid'], row['year'],
                                row['rep'], row['tillage'], row['rotation'])
        if not data.has_key(key):
            data[key] = {}
        data[key][row['varname']] = row["value"]

    res = ("uniqueid,plotid,year,rep,tillage,rotation,agr1,agr2,agr7,"
          +"agr15,agr16,agr17,agr19\n")
    for key in data.keys():
        tokens = key.split("|")
        res += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (tokens[0], tokens[1],
                tokens[2], tokens[3], tokens[4], tokens[5], 
                data[key].get('AGR1', ''), data[key].get('AGR2', ''),
                data[key].get('AGR7', ''), data[key].get('AGR15', ''),
                data[key].get('AGR16', ''), data[key].get('AGR16', ''),
                data[key].get('AGR17', ''), data[key].get('AGR18', ''))
    
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
