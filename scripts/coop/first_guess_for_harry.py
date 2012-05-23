"""
 Generate a first guess file for Harry Hillaker to use for the monthly COOP
 QC, will hopefully save him some time...

sites = []
for line in open('/tmp/SCIA1107.txt'):
    tokens = line.split(",")
    if tokens[0] in ["", "2011", "YR"]:
        continue
    site = "IA%04i" % (int(tokens[0]),)
    if not site in sites:
        sites.append( site )
    
print `sites`
sys.exit()
"""

import sys
import mx.DateTime
import iemdb
from xlwt import Workbook
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

SITES = ['IA0112', 'IA0133', 'IA0157', 'IA0197', 'IA0200', 'IA0203', 'IA0241', 
         'IA0364', 'IA0385', 'IA0536', 'IA0576', 'IA0600', 'IA0608', 'IA0745', 
         'IA0753', 'IA0807', 'IA0910', 'IA0923', 'IA0933', 'IA1126', 'IA1063', 
         'IA1233', 'IA1257', 'IA1277', 'IA1314', 'IA1319', 'IA1354', 'IA1394', 
         'IA1402', 'IA1442', 'IA1533', 'IA1541', 'IA1635', 'IA0149', 'IA1704', 
         'IA1705', 'IA0512', 'IA1833', 'IA1954', 'IA1962', 'IA2070', 'IA2110', 
         'IA2171', 'IA2203', 'IA2209', 'IA2235', 'IA2299', 'IA2311', 'IA2364', 
         'IA2367', 'IA2638', 'IA2573', 'IA2603', 'IA2689', 'IA2723', 'IA2724', 
         'IA7892', 'IA2789', 'IA2864', 'IA2977', 'IA2999', 'IA3007', 'IA3120', 
         'IA3288', 'IA3438', 'IA3473', 'IA3487', 'IA3509', 'IA3517', 'IA3584', 
         'IA4094', 'IA3632', 'IA3718', 'IA3909', 'IA2041', 'IA3675', 'IA4063', 
         'IA4101', 'IA4106', 'IA4142', 'IA4228', 'IA4244', 'IA4308', 'IA4874', 
         'IA4381', 'IA4389', 'IA4502', 'IA4557', 'IA4585', 'IA4587', 'IA4624', 
         'IA4705', 'IA4735', 'IA4758', 'IA4894', 'IA4926', 'IA4963', 'IA5086', 
         'IA5123', 'IA5131', 'IA5198', 'IA5199', 'IA5230', 'IA5235', 'IA5250', 
         'IA5493', 'IA5876', 'IA0001', 'IA5650', 'IA5769', 'IA5796', 'IA5837', 
         'IA5952', 'IA5992', 'IA6103', 'IA6151', 'IA6160', 'IA6190', 'IA6199', 
         'IA0002', 'IA6243', 'IA6305', 'IA6316', 'IA6327', 'IA6389', 'IA6273', 
         'IA6527', 'IA6566', 'IA6719', 'IA7326', 'IA6766', 'IA6800', 'IA6891', 
         'IA6910', 'IA6940', 'IA7147', 'IA7152', 'IA7161', 'IA7312', 'IA7386', 
         'IA7594', 'IA7613', 'IA7664', 'IA7669', 'IA7678', 'IA7700', 'IA7708', 
         'IA7859', 'IA0003', 'IA7726', 'IA7842', 'IA7844', 'IA8009', 'IA7979', 
         'IA8026', 'IA8062', 'IA8296', 'IA8339', 'IA8568', 'IA8668', 'IA8688', 
         'IA8706', 'IA8755', 'IA8806', 'IA9067', 'IA9132', 'IA9750', 'IA8410', 
         'IA8693']

def get_site(year, month, site):
    """
    do our work for this site
    """
    # Create data dictionary to store our wares
    data = [0,]
    sts = mx.DateTime.DateTime(year, month, 1)
    ets = sts + mx.DateTime.RelativeDateTime(months=1)
    while sts < ets:
        data.append({'coop': {'high': '', 'low': '', 'atob': '', 
                              'prec': '', 'sf': '', 'sog': ''},
                     'iemre': {'high': '', 'low': '', 'atob': '', 
                              'prec': '', 'sf': '', 'sog': ''}})
        sts += mx.DateTime.RelativeDateTime(days=1)
    # Figure out the COOP NWSLI for this site
    mcursor.execute(""" select id, ST_distance(
    (select geom from stations where network = 'IACLIMATE' and id = %s), 
    geom) from stations where network = 'IA_COOP' and climate_site = %s 
    ORDER by st_distance ASC LIMIT 1""", (site, site))
    if mcursor.rowcount == 0:
        print 'ERROR', site
        return data
    nwsli = mcursor.fetchone()[0]

    # Go fetch COOP obs
    icursor.execute("""
    select extract(day from day), s.max_tmpf, s.min_tmpf, s.snow, s.snowd, 
    s.coop_tmpf, s.pday from summary_%s s JOIN stations t on (t.iemid = s.iemid) 
    WHERE t.id = '%s' and extract(month from day) = %s
    """ % (year, nwsli, month))
    for row in icursor:
        idx = int(row[0])
        data[idx]['coop']['high'] = row[1]
        data[idx]['coop']['low'] = row[2]
        data[idx]['coop']['atob'] = row[5]
        data[idx]['coop']['sf'] = row[3]
        data[idx]['coop']['sog'] = row[4]
        data[idx]['coop']['prec'] = row[6]

    # Go Fetch IEMRE
    ccursor.execute("""
    select extract(day from day), high, low, snow, snowd, precip from 
    alldata_ia where station = %s and year = %s and month = %s
    """, (site, year, month))
    for row in ccursor:
        idx = int(row[0])
        data[idx]['iemre']['high'] = row[1]
        data[idx]['iemre']['low'] = row[2]
        data[idx]['iemre']['sf'] = row[3]
        data[idx]['iemre']['sog'] = row[4]
        data[idx]['iemre']['prec'] = row[5]

    return data

def get_sitename(site):
    mcursor.execute("""SELECT name from stations where network = 'IACLIMATE'
    and id = %s """, (site,))
    if mcursor.rowcount == 0:
        return site
    return mcursor.fetchone()[0]

def print_data(year, month, site, sheet, data):
    """
    Print out our data file!
    """
    row = sheet.row(0)
    row.write(8, '?')
    row.write(10, '?')
    row.write(12, get_sitename(site))
    row = sheet.row(1)
    row.write(2, 'YR')
    row.write(3, 'MO')
    row.write(4, 'DA')
    row.write(6, 'MAX')
    row.write(8, 'MIN')
    row.write(10, 'ATOB')
    row.write(12, 'PREC')
    row.write(14, 'SF')
    row.write(16, 'SOG')
    row.write(17, 'F')
    row.write(18, 'I')
    row.write(19, 'G')
    row.write(20, 'T')
    row.write(21, 'H')
    row.write(22, 'W')

    sts = mx.DateTime.DateTime(year, month, 1)
    ets = sts + mx.DateTime.RelativeDateTime(months=1)
    while sts < ets:
        idx = int(sts.day)
        row = sheet.row(idx+1)
        row.write(0, '%s' % (int(site[2:]),))
        row.write(2, year)
        row.write(3, month)
        row.write(4, sts.day)
        row.write(5, data[idx]['iemre']['high'])
        row.write(6, data[idx]['coop']['high'])
        row.write(7, data[idx]['iemre']['low'])
        row.write(8, data[idx]['coop']['low'])
        row.write(10, data[idx]['coop']['atob']) 
        row.write(11, data[idx]['iemre']['prec'])
        row.write(12, data[idx]['coop']['prec'])
        row.write(13, data[idx]['iemre']['sf'])
        row.write(14, data[idx]['coop']['sf'])
        row.write(15, data[idx]['iemre']['sog'])
        row.write(16, data[idx]['coop']['sog'])
        sts += mx.DateTime.RelativeDateTime(days=1)

def runner(year, month):
    """
    Actually generate a text file for the given month
    """
    book = Workbook()
    for site in SITES:
        data = get_site(year, month, site)
        sheet = book.add_sheet(site[2:])
        sheet.col(0).width = 256*5
        sheet.col(1).width = 256*2
        sheet.col(2).width = 256*5
        sheet.col(3).width = 256*4
        sheet.col(4).width = 256*4
        for col in range(5,17):
            sheet.col(col).width = 256*5
        print_data( year, month, site, sheet, data)
    book.save("IEM%s%s.xlsx" % (year, month))

if __name__ == '__main__':
    runner(int(sys.argv[1]), int(sys.argv[2]))
