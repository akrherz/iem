#!/usr/bin/env python

import sys
import psycopg2
import cgi
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

ALL = " ALL SITES"
varorder = []
varlookup = {}

COVER_SITES = ['MASON', 'KELLOGG', 'GILMORE', 'ISUAG', 'WOOSTER.COV',
               'SEPAC', 'BRADFORD.B1', 'BRADFORD.B2',
               'BRADFORD.C', 'FREEMAN']

def main():
    sys.stdout.write('Content-type: text/html\n\n')

    table = ""
    cursor.execute("""SELECT uniqueid, valid, cropyear, operation from operations
    WHERE operation in ('harvest_corn', 'harvest_soy', 'plant_rye',
    'plant_rye-corn-res', 'plant_rye-soy-res')""")
    data = {}
    for row in cursor:
        site = row[0]
        valid = row[1]
        cropyear = str(row[2])
        operation = row[3]
        if not data.has_key(site):
            data[site] = {'2011': {}, '2012': {}, '2013': {}, '2014': {},
                          '2015': {}}
        if not data[site].has_key(cropyear):
            data[site][cropyear] = {'harvest_soy': '','harvest_corn': '',
                                    'plant_rye': '', 'plant_rye-corn-res': '',
                                    'plant_rye-soy-res': ''}
        data[site][cropyear][operation] = valid
        if operation == 'plant_rye':
            for op2 in ['plant_rye-soy-res', 'plant_rye-corn-res']:
                data[site][cropyear][op2] = valid
        
    sys.stderr.write(str(data))
        
    for site in COVER_SITES: #data.keys():
        table += "<tr><td>%s</td>" % (site,)
        for yr in ['2011', '2012', '2013', '2014', '2015']:
            for op in ['harvest_corn', 'harvest_soy']:
                table += "<td>%s</td>" % (
                        data[site].get(yr, {}).get(op, ''),)
            yr2 = str(int(yr)+1)
            for op in ['plant_rye-corn-res', 'plant_rye-soy-res']:
                table += "<td>%s</td>" % (
                        data[site].get(yr2, {}).get(op, ''),)
        table += "</tr>"

    sys.stdout.write("""<!DOCTYPE html>
<html lang='en'>
<head>
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-override.css" rel="stylesheet">
</head>    
<body>

<table class="table table-striped table-bordered">
<thead>
 <tr>
  <th rowspan="3">Site</th>
  <th colspan="4">2011-2012</th>
  <th colspan="4">2012-2013</th>
  <th colspan="4">2013-2014</th>
  <th colspan="4">2014-2015</th>
  <th colspan="4">2015-2016</th>
 </tr>
 <tr>
  <th colspan="2">cash harvest</th>
  <th colspan="2">cover seeding</th>
  <th colspan="2">cash harvest</th>
  <th colspan="2">cover seeding</th>
  <th colspan="2">cash harvest</th>
  <th colspan="2">cover seeding</th>
  <th colspan="2">cash harvest</th>
  <th colspan="2">cover seeding</th>
  <th colspan="2">cash harvest</th>
  <th colspan="2">cover seeding</th>
 </tr>
 <tr>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
  <th>Corn</th><th>Soybean</th>
 </tr>
</thead>
%s
</table>

</body>
</html>
    """ % (table,))
    
if __name__ == '__main__':
    main()