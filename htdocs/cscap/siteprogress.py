#!/usr/bin/env python
import sys
import psycopg2
import cgi
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb',
                          user='nobody')
cursor = DBCONN.cursor()


def get_data(mode, data):
    ''' Do stuff '''
    table = 'agronomic_data' if mode == 'agronomic' else 'soil_data'
    cursor.execute("""SELECT site,
    -- We have some number
    sum(case when lower(value) not in ('.','','did not collect','n/a') and
        value is not null then 1 else 0 end),
    -- Periods
    sum(case when lower(value) in ('.') then 1 else 0 end),
    -- We have some value, not a number
    sum(case when lower(value) in ('did not collect', 'n/a')
        then 1 else 0 end),
    -- We have a null
    sum(case when value is null then 1 else 0 end),
    count(*) from """+table+"""
    WHERE (value is Null or lower(value) != 'n/a')
    GROUP by site""")
    for row in cursor:
        for site in [row[0], '_ALL']:
            entry = data.setdefault(site, dict(hits=0, dots=0, other=0,
                                               nulls=0, tot=0))
            entry['hits'] += row[1]
            entry['dots'] += row[2]
            entry['other'] += row[3]
            entry['nulls'] += row[4]
            entry['tot'] += row[5]


def make_progress(row):
    ''' return string for progress bar '''
    if row is None:
        return ''
    hits = row['hits'] / float(row['tot']) * 100.0
    dots = row['dots'] / float(row['tot']) * 100.0
    other = row['other'] / float(row['tot']) * 100.0
    nulls = row['nulls'] / float(row['tot']) * 100.0
    return """<div class="progress">
  <div class="progress-bar progress-bar-success" style="width: %.1f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-info" style="width: %.1f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-warning" style="width: %.1f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-danger" style="width: %.1f%%">
    <span>%s</span>
  </div>
</div>""" % (hits - 0.05, row['hits'], dots - 0.05, row['dots'],
             other - 0.05, row['other'],
             nulls - 0.05, row['nulls'])

if __name__ == '__main__':
    sys.stdout.write('Content-type: text/html\n\n')
    form = cgi.FieldStorage()
    mode = form.getfirst('mode', 'agronomic')
    data = {}
    get_data('agronomic', data)
    get_data('soils', data)

    sites = data.keys()
    sites.sort()
    sys.stdout.write("""<!DOCTYPE html>
<html lang='en'>
<head>
<link href="/vendor/bootstrap/3.3.5/css/bootstrap.min.css" rel="stylesheet">
    <title>CSCAP Research Site Agronomic+Soils Data Progress</title>
    </head>
    <body>
    <style>
    .progress{
     margin-bottom: 0px;
    }
    .progress-bar {
    z-index: 1;
 }
.progress span {
    color: black;
    z-index: 2;
 }
    </style>
    <span>Key:</span>
    <span class="btn btn-success">has data</span>
    <span class="btn btn-info">periods</span>
    <span class="btn btn-warning">did not collect</span>
    <span class="btn btn-danger">no entry / empty</span>

    <p>This page lists the data progress for Agronomic + Soils variables
    collected by the Google Spreadsheets. These values are valid for the
    duration of the project 2011-2015.</p>

<table class='table table-striped table-bordered'>
<thead><tr>
    <th width="20%">SiteID</th>
    <th width="60%">Progress</th>
    <th width="10%">Count</th>
    <th width="10%">Percent Done (green + orange)</th>
</tr></thead>
    """)
    for sid in sites:
        if sid == '_ALL':
            continue
        sys.stdout.write("""<tr><th>%s</th>""" % (sid,))
        row = data[sid]
        sys.stdout.write('<td>%s</td>' % (make_progress(row)))
        sys.stdout.write("<td>%.0f</td>" % (row['tot'], ))
        sys.stdout.write("<td>%.2f%%</td>" % (((row['hits'] + row['other']) /
                                               float(row['tot'])) * 100.))
        sys.stdout.write("</tr>\n\n")
    sid = "_ALL"
    sys.stdout.write("""<tr><th>%s</th>""" % (sid,))
    row = data[sid]
    sys.stdout.write('<td>%s</td>' % (make_progress(row)))
    sys.stdout.write("<td>%.0f</td>" % (row['tot'], ))
    sys.stdout.write("<td>%.2f%%</td>" % (((row['hits'] + row['other']) /
                                           float(row['tot'])) * 100.))
    sys.stdout.write("</tr>\n\n")
    sys.stdout.write("</table>")
