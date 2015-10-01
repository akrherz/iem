#!/usr/bin/env python
''' Print out a big thing of progress bars, gasp '''

import sys
import psycopg2
import cgi
DBCONN = psycopg2.connect(database='sustainablecorn', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

ALL = " ALL SITES"
varorder = []
varlookup = {}

def build_vars(mode):
    ''' build vars '''
    sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/cscap')
    import util
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('/mesonet/www/apps/iemwebsite/scripts/cscap/mytokens.cfg')
    spr_client = util.get_spreadsheet_client(config)
    feed = spr_client.get_list_feed(config.get('cscap', 'sdckey'), 'od6')
    places = 3 if mode != 'soil' else 4
    prefix = 'AGR' if mode != 'soil' else 'SOIL'
    for entry in feed.entry:
        data = entry.to_dict()
        if data['key'] is None or data['key'][:places] != prefix:
            continue
        varorder.append( data['key'].strip() )
        varlookup[ data['key'].strip() ] = data['name'].strip()
    

def get_data(year, mode):
    ''' Do stuff '''
    data = {ALL: {} }
    dvars = []
    table = 'agronomic_data' if mode == 'agronomic' else 'soil_data'
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
    count(*) from """+table+"""
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
</div>""" % (hits - 0.05, row['hits'], dots - 0.05, row['dots'], 
             other - 0.05, row['other'],
             nulls - 0.05, row['nulls'])

if __name__ == '__main__':
    sys.stdout.write('Content-type: text/html\n\n')
    form = cgi.FieldStorage()
    year = int(form.getfirst('year', 2011))
    mode = form.getfirst('mode', 'agronomic')
    build_vars(mode)

    data, dvars = get_data(year, mode)

    sites = data.keys()
    sites.sort()
    sys.stdout.write("""<!DOCTYPE html>
    <html lang='en'>
    <head>
    <link href="/vendor/bootstrap/3.3.5/css/bootstrap.min.css" rel="stylesheet">
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

<div class="row well">
    <div class="col-md-4 col-sm-4">Select Mode:</div>
    <div class="col-md-4 col-sm-4">
        <a href="dataprogress.py?mode=agronomic">Agronomic Data</a>
    </div>
    <div class="col-md-4 col-sm-4">
        <a href="dataprogress.py?mode=soil">Soil Data</a>
    </div>
</div>
    
    <form method="GET" name='theform'>
    <input type="hidden" name="mode" value="%s" />
    Select Year; <select name="year">
    """ % (mode,))
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
    <span class="btn btn-warning">did not collect</span>
    <span class="btn btn-danger">no entry / empty</span>
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