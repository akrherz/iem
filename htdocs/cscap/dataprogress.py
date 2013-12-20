#!/usr/bin/env python
''' Print out a big thing of progress bars, gasp '''

import sys
import psycopg2
import cgi
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

ALL = " ALL SITES"

varhack = """   [1] Corn final plant population
[2] Soybean final plant population
   [3] Mid-season canopy N sensing
   [4] Corn vegetative biomass at R6 (dry) 
[32] Corn cob biomass at R6 (dry)
[33] Corn grain biomass at R6 (dry)
[5] Soybean vegetative biomass at R8 (stems and pods only; no leaves)
[34] Soybean grain biomass at R8 (dry)
[6] Cover crop (rye) biomass in late fall (no significant weeds)
[37] Cover crop (rye) and weedy biomass in late fall
[38] Weedy biomass (only) in late fall
[7] Cover crop (rye) biomass at termination (spring) (no significant weeds)
[39] Cover crop (rye) and weedy biomass at termination (spring)
[40] Weedy biomass (only) at termination (spring)
   [8] Wheat plant biomass at maturity 
   [9] Corn vegetative biomass total carbon at R6
   [10] Corn vegetative biomass total nitrogen at R6 
[11] Soybean vegetative biomass total carbon at R8
[12] Soybean vegetative biomass total nitrogen at R8
   [13] Rye biomass total carbon at fall
   [14] Rye biomass total nitrogen at fall
   [15] Rye biomass total carbon at spring
   [16] Rye biomass total nitrogen at spring
[41] Red clover (or miscelaneous) cover crop biomass
[42] Red clover (or miscelaneous) cover crop total nitrogen
[43] Red clover (or miscelaneous) cover crop total carbon
   [17] Corn grain yield at 15.5% MB
   [18] Corn grain moisture
   [19] Soybean grain yield at 13.0% MB
   [20] Soybean grain moisture
   [21] Wheat grain yield at 13.5% MB
   [22] Wheat grain moisture
   [23] Corn grain total carbon at R6
   [24] Corn cob total carbon at R6
   [25] Corn grain total nitrogen at R6
   [26] Corn cob total nitrogen at R6
   [27] Soybean grain total carbon at R8
   [28] Soybean grain total nitrogen at R8
   [29] Wheat grain total carbon at maturity
   [30] Wheat grain total nitrogen at maturity
   [31] Corn stalk nitrate samples"""
varorder = []
varlookup = {}
for line in varhack.split("\n"):
    val = line.strip().split()[0].replace("[","").replace("]","")
    varorder.append( "AGR%s" % (val,))
    varlookup[ "AGR%s" % (val,) ] = line.strip()

def get_data(year):
    ''' Do stuff '''
    data = {ALL: {} }
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
    WHERE year = %s and (value is Null or lower(value) != 'n/a') GROUP by site, varname""", (year,))
    for row in cursor:
        if row[1] not in dvars:
            dvars.append( row[1] )
        if not data.has_key(row[0]):
            data[row[0]] = {}
        data[row[0]][row[1]] = {'hits': row[2], 'dots': row[3], 
                                'other': row[4], 'nulls': row[5],
                                'tot': row[6]}
        if not data[ALL].has_key(row[1]):
            data[ALL][row[1]] = {'hits': 0, 'dots': 0, 'other': 0,
                                    'nulls': 0, 'tot': 0}
        data[ALL][row[1]]['hits'] += row[2]
        data[ALL][row[1]]['dots'] += row[3]
        data[ALL][row[1]]['other'] += row[4]
        data[ALL][row[1]]['nulls'] += row[5]
        data[ALL][row[1]]['tot'] += row[6]
    
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
</div>""" % (hits, row['hits'], dots, row['dots'], other, row['other'], 
             nulls, row['nulls'])

if __name__ == '__main__':
    sys.stdout.write('Content-type: text/html\n\n')
    
    form = cgi.FieldStorage()
    year = int(form.getfirst('year', 2011))
    
    data, dvars = get_data(year)

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
    dvars = varorder
    if len(ids) > 0:
        dvars = ids
    for varid in varorder:
        checked = ""
        if varid in ids:
            checked = "checked='checked'"
        sys.stdout.write("""<input type='checkbox' name='ids' 
        value='%s'%s><abbr title="%s">%s</abbr></input> &nbsp; """ % (varid, 
                                            checked, varlookup[varid], varid))
    
    sys.stdout.write("""
    <input type="submit" value="Generate Table">
    </form>
    <span>Key:</span>
    <span class="btn btn-success">has data</span>
    <span class="btn btn-info">periods</span>
    <span class="btn btn-warning">DNC empty</span>
    <span class="btn btn-danger">no entry</span>
    <table class='table table-striped table-bordered'>
    
    """)
    sys.stdout.write("<thead><tr><th>SiteID</th>")
    for dv in dvars:
        sys.stdout.write("""<th><abbr title="%s">%s</abbr></th>""" % (
                                                varlookup[dv], dv))
    sys.stdout.write("</tr></thead>")
    for sid in sites:
        sys.stdout.write("""<tr><th>%s</th>""" % (sid,))
        for datavar in dvars:
            row = data[sid].get(datavar, None)
            sys.stdout.write('<td>%s</td>' % (make_progress(row)))
        sys.stdout.write("</tr>\n\n")
    sys.stdout.write("</table>")
    
    sys.stdout.write("""
    <h3>Data summary for all sites included</h3>
    <p>
    <span>Key:</span>
    <span class="btn btn-success">has data</span>
    <span class="btn btn-info">periods</span>
    <span class="btn btn-warning">DNC empty</span>
    <span class="btn btn-danger">no entry</span>
    <table class='table table-striped table-bordered'>
    <thead><tr><th width="33%%">Variable</th><th width="66%%">%s</th></tr>
    """ % (ALL,))
    for datavar in dvars:
        row = data[ALL].get(datavar, None)
        sys.stdout.write("<tr><th>%s %s</th><td>%s</td></tr>" % (
                                                    datavar, varlookup[datavar],
                                                        make_progress(row)))
    
    sys.stdout.write('</table></p>')