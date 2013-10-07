'''
 Load the visit history CSV and then add the following columns:
  
  - ames
'''
import psycopg2
import datetime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

def find_climate_site(lon, lat):
    ''' Figure out the climate site id closest to this lon, lat pair '''
    cursor.execute("""
    select ST_Distance(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist, 
    id from stations where network ~* 'CLIMATE' ORDER by dist ASC LIMIT 8
    """ % (lon, lat))
    stations = []
    for row in cursor:
        stations.append( row[1].lower() )
    return stations

o = open('visit_history_093013_st12_daryl.csv', 'w')
o.write(('"univ_id","apltn_type","actvy_datedb","actvy_type","vis_month",'
    +'"vis_year","entry_ccyy","sem_num","entry_sem_cd","actn_cd","clsfn_yr",'
    +'"entry_year","hs_status","city","st","cntry","zip_5","lat","lon",'
    +'"ames_high","ames_precip","ames_clhigh","ames_clprecip",'
    +'"remote_clhigh","remote_clprecip","wxhigh_score","wxprecip_score"\n'))

def add_cols(line, addon):
    ''' Addon additional columns '''
    wxprecip = 'M'
    wxhigh = 'M'
    if addon['remote_clhigh'] != 'M':
        wxhigh = float(abs(addon['remote_clhigh'] - addon['ames_high'])) / 5.0
        wxhigh = '%.0f' % (wxhigh,)
        if addon['ames_clprecip'] > addon['remote_clprecip']:
            # Ames is wetter, so if it rains...
            if addon['ames_precip'] > 0:
                wxprecip = 1
        else:
            if addon['ames_precip'] == 0:
                wxprecip = 0
    
    o.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (line.strip(), addon['ames_high'],
                                addon['ames_precip'], addon['ames_clhigh'],
                                addon['ames_clprecip'], addon['remote_clhigh'],
                                addon['remote_clprecip'], wxhigh, wxprecip))

for line in open('visit_history_093013_st12.csv'):
    addon = {'ames_high': 'M', 'ames_precip': 'M', 
             'ames_clhigh': 'M', 'ames_clprecip': 'M',
             'remote_clhigh': 'M', 'remote_clprecip': 'M'}
    tokens = line.strip().split(",")
    lat = tokens[17]
    lon = tokens[18]
    if lon == '"lon"':
        continue
    if lon == '' or lat == '':
        add_cols(line, addon)
        continue
    stations = find_climate_site(lon, lat)
    
    # Figure out date
    ts = datetime.datetime.strptime(tokens[2], '%m/%d/%Y')

    # Get Ames high and precip
    cursor.execute("""SELECT high, precip from alldata_ia where station = 'IA0200'
    and day = '%s'""" % (ts.strftime("%Y-%m-%d"),))
    row = cursor.fetchone()
    addon['ames_high'] = row[0]
    addon["ames_precip"] = row[1]
    
    # Get Ames Climate
    cursor.execute("""SELECT high, precip from ncdc_climate81 where station = 'ia0200'
    and valid = '2000-%s'""" % (ts.strftime("%m-%d"),))
    row = cursor.fetchone()
    addon['ames_clhigh'] = row[0]
    addon["ames_clprecip"] = row[1]
    
    # Get climate?
    cursor.execute("""SELECT high, precip from ncdc_climate81 where valid = '2000-%s'
    and station in %s""" % (ts.strftime("%m-%d"), str(tuple(stations))))
    if cursor.rowcount == 0:
        print 'uh oh', ts, stations
        add_cols(line, addon)
        continue
    
    row = cursor.fetchone()
    addon['remote_clhigh'] = row[0]
    addon['remote_clprecip'] = row[1]
    
    add_cols(line, addon)
    
o.close()