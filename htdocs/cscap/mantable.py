#!/usr/bin/env python

import sys
import psycopg2
import cgi
import subprocess
import os
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

ALL = " ALL SITES"
varorder = []
varlookup = {}

COVER_SITES = ['MASON', 'KELLOGG', 'GILMORE', 'ISUAG', 'WOOSTER.COV',
               'SEPAC', 'BRADFORD.B1', 'BRADFORD.B2',
               'BRADFORD.C', 'FREEMAN']

def reload_data():
    """ Run the sync script to download data from Google """
    os.chdir("/mesonet/www/apps/iemwebsite/scripts/cscap")
    p = subprocess.Popen("python harvest_management.py", shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return "<div class=\"alert alert-info\"><pre>%s %s</pre></div>" % (
                                        p.stdout.read(), p.stderr.read())

def main():
    sys.stdout.write('Content-type: text/html\n\n')

    form = cgi.FieldStorage()
    reloadres = "<a href=\"mantable.py?reload=yes\" class=\"btn btn-default\">Request Sync of Google Data</a>"
    if form.getfirst('reload') is not None:
        reloadres += reload_data()

    cursor.execute("""
        SELECT uniqueid, valid, cropyear, operation from operations
        WHERE operation in ('harvest_corn', 'harvest_soy', 'plant_rye',
        'plant_rye-corn-res', 'plant_rye-soy-res', 'sample_soilnitrate',
        'sample_covercrop', 'termination_rye_corn', 'termination_rye_soy')
        ORDER by valid ASC
    """)
    data = {}
    for row in cursor:
        site = row[0]
        valid = row[1]
        cropyear = str(row[2])
        operation = row[3]
        if not data.has_key(site):
            data[site] = {}
            for cy in ['2011', '2012', '2013', '2014','2015']:
                data[site][cy] = {'harvest_soy': '','harvest_corn': '',
                                    'plant_rye': '', 'plant_rye-corn-res': '',
                                    'plant_rye-soy-res': '',
                                    'fall_sample_soilnitrate_corn': '',
                                    'fall_sample_soilnitrate_soy': '',
                                    'spring_sample_soilnitrate_corn': '',
                                    'spring_sample_soilnitrate_soy': '',
                                    'termination_rye_corn': '',
                                    'termination_rye_soy': '',
                                    'spring_sample_covercrop_corn': '',
                                    'spring_sample_covercrop_soy': '',
                                    'fall_sample_covercrop_corn': '',
                                    'fal_sample_covercrop_soy': '',
                }
        if operation == 'plant_rye':
            for op2 in ['plant_rye-soy-res', 'plant_rye-corn-res']:
                data[site][cropyear][op2] = valid
        elif operation in ['sample_soilnitrate', 'sample_covercrop']:
            # We only want 'fall' events
            season = 'fall_'
            if valid.month < 8:
                season = 'spring_'
            if data[site][cropyear][season+operation+'_soy'] != '':
                data[site][cropyear][season+operation+'_corn'] = valid
            else:
                data[site][cropyear][season+operation+'_soy'] = valid
        else:
            data[site][cropyear][operation] = valid

    table = ""
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

    #---------------------------------------------------------------
    table2 = ""
    for site in COVER_SITES: #data.keys():
        table2 += "<tr><td>%s</td>" % (site,)
        for yr in ['2011', '2012', '2013', '2014', '2015']:
            for op in ['fall_sample_soilnitrate_corn',
                       'fall_sample_soilnitrate_soy']:
                table2 += "<td>%s</td>" % (
                        data[site].get(yr, {}).get(op, ''),)
            yr2 = str(int(yr)+1)
            for op in ['fall_sample_covercrop_corn', 
                       'fall_sample_covercrop_soy']:
                table2 += "<td>%s</td>" % (
                        data[site].get(yr2, {}).get(op, ''),)
        table2 += "</tr>"

    #---------------------------------------------------------------
    table3 = ""
    for site in COVER_SITES: #data.keys():
        table3 += "<tr><td>%s</td>" % (site,)
        for yr in ['2012', '2013', '2014', '2015']:
            for op in ['spring_sample_soilnitrate_corn',
                       'spring_sample_soilnitrate_soy']:
                table3 += "<td>%s</td>" % (
                        data[site].get(yr, {}).get(op, ''),)
            for op in ['spring_sample_covercrop_corn',
                       'spring_sample_covercrop_soy']:
                table3 += "<td>%s</td>" % (
                        data[site].get(yr, {}).get(op, ''),)
            for op in ['termination_rye_corn', 'termination_rye_soy']:
                table3 += "<td>%s</td>" % (
                        data[site].get(yr, {}).get(op, ''),)
        table3 += "</tr>"

    sys.stdout.write("""<!DOCTYPE html>
<html lang='en'>
<head>
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-override.css" rel="stylesheet">
</head>    
<body>

%s

<h3>Sub Table 1</h3>

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

<h3>Sub Table 2</h3>

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
  <th colspan="2">Fall Soil Nitrate</th>
  <th colspan="2">Fall Cover Crop Sample</th>
  <th colspan="2">Fall Soil Nitrate</th>
  <th colspan="2">Fall Cover Crop Sample</th>
  <th colspan="2">Fall Soil Nitrate</th>
  <th colspan="2">Fall Cover Crop Sample</th>
  <th colspan="2">Fall Soil Nitrate</th>
  <th colspan="2">Fall Cover Crop Sample</th>
  <th colspan="2">Fall Soil Nitrate</th>
  <th colspan="2">Fall Cover Crop Sample</th>
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

<h3>Sub Table 3</h3>

<table class="table table-striped table-bordered">
<thead>
 <tr>
  <th rowspan="3">Site</th>
  <th colspan="6">Spring 2012</th>
  <th colspan="6">Spring 2013</th>
  <th colspan="6">Spring 2014</th>
  <th colspan="6">Spring 2015</th>
 </tr>
 <tr>
  <th colspan="2">Rye Sampling (spring)</th>
  <th colspan="2">Soil N Sampling (spring)</th>
  <th colspan="2">Termination</th>
  <th colspan="2">Rye Sampling (spring)</th>
  <th colspan="2">Soil N Sampling (spring)</th>
  <th colspan="2">Termination</th>
  <th colspan="2">Rye Sampling (spring)</th>
  <th colspan="2">Soil N Sampling (spring)</th>
  <th colspan="2">Termination</th>
  <th colspan="2">Rye Sampling (spring)</th>
  <th colspan="2">Soil N Sampling (spring)</th>
  <th colspan="2">Termination</th>
 </tr>
 <tr>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
  <th>before C</th><th>before S</th>
 </tr>
</thead>
%s
</table>

</body>
</html>
    """ % (reloadres, table, table2, table3))
    
if __name__ == '__main__':
    main()