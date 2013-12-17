#!/usr/bin/env python
''' Print out a big thing of progress bars, gasp '''

import sys
import psycopg2
import cgi
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb')
cursor = DBCONN.cursor()

def get_data(year):
    ''' Do stuff '''
    data = {' ALL': {} }
    dvars = []
    cursor.execute("""SELECT site, varname, 
    -- We have some number
    sum(case when lower(value) not in ('.','','did not collect','n/a') and
        value is not null then 1 else 0 end),
    -- Periods
    sum(case when lower(value) in ('.') then 1 else 0 end),
    -- We have some value, not a number
    sum(case when lower(value) in ('did not collect', 'n/a') then 1 else 0 end),
    -- We have a null
    sum(case when value is null then 1 else 0 end),
    count(*) from agronomic_data
    WHERE year = %s GROUP by site, varname""", (year,))
    for row in cursor:
        if row[1] not in dvars:
            dvars.append( row[1] )
        if not data.has_key(row[0]):
            data[row[0]] = {}
        data[row[0]][row[1]] = {'hits': row[2], 'dots': row[3], 
                                'other': row[4], 'nulls': row[5],
                                'tot': row[6]}
        if not data[' ALL'].has_key(row[1]):
            data[' ALL'][row[1]] = {'hits': 0, 'dots': 0, 'other': 0,
                                    'nulls': 0, 'tot': 0}
        data[' ALL'][row[1]]['hits'] += row[2]
        data[' ALL'][row[1]]['dots'] += row[3]
        data[' ALL'][row[1]]['other'] += row[4]
        data[' ALL'][row[1]]['nulls'] += row[5]
        data[' ALL'][row[1]]['tot'] += row[6]
    
    return data, dvars

def make_progress(row):
    ''' return string for progress bar '''
    if row is None:
        return ''
    hits = row['hits'] / float(row['tot']) * 100.0
    dots = row['dots'] / float(row['tot']) * 100.0
    other = row['other'] / float(row['tot']) * 100.0
    nulls = row['nulls'] / float(row['tot']) * 100.0
    return """<div class="progress">
  <div class="progress-bar progress-bar-success" style="width: %.0f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-info" style="width: %.0f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-warning" style="width: %.0f%%">
    <span>%s</span>
  </div>
  <div class="progress-bar progress-bar-danger" style="width: %.0f%%">
    <span>%s</span>
  </div>
</div>""" % (hits, row['hits'], dots, row['dots'], other, row['other'], 
             nulls, row['nulls'])

if __name__ == '__main__':
    sys.stdout.write('Content-type: text/html\n\n')
    
    form = cgi.FieldStorage()
    year = int(form.getfirst('year', 2011))
    
    data, dvars = get_data(year)
    dvars.sort()
    sites = data.keys()
    sites.sort()
    sys.stdout.write("""<!DOCTYPE html>
    <html lang='en'>
    <head>
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-override.css" rel="stylesheet">
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
    <form method="GET" name='theform'>
    
    Select Year; <select name="year">
    """)
    for yr in range(2011,2016):
        checked = ''
        if year == yr:
            checked = " selected='selected'"
        sys.stdout.write("""<option value="%s" %s>%s</option>\n""" % (yr, 
                                                            checked, yr))
    
    sys.stdout.write("</select><br />")
    
    ids = form.getlist('ids')
    if len(ids) > 0:
        dvars = ids
    for i in range(1, 44):
        checked = ''
        if "AGR%s" % (i,) in ids:
            checked = "checked='checked'"
        sys.stdout.write("""<input type='checkbox' name='ids' 
        value='AGR%s'%s>AGR%s</input> &nbsp; """ % (i, checked, i))
    
    sys.stdout.write("""
    <input type="submit" value="Generate Table">
    </form>
    <span>Key:</span>
    <span class="btn btn-success">has data</span>
    <span class="btn btn-info">periods</span>
    <span class="btn btn-warning">n/a DNC empty</span>
    <span class="btn btn-danger">no entry</span>
    <table class='table table-striped table-bordered'>
    
    """)
    sys.stdout.write("<thead><tr><th>SiteID</th>")
    for dv in dvars:
        sys.stdout.write("<th>%s</th>" % (dv,))
    sys.stdout.write("</tr></thead>")
    for sid in sites:
        sys.stdout.write("""<tr><th>%s</th>""" % (sid,))
        for datavar in dvars:
            row = data[sid].get(datavar, None)
            sys.stdout.write('<td>%s</td>' % (make_progress(row)))
        sys.stdout.write("</tr>\n\n")
    sys.stdout.write("</table>")
    
    print '</p>'