import psycopg2
import pyiem.meteorology as met
from pyiem.datatypes import temperature
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))

def get(station):
    cursor.execute("""
      SELECT valid, sknt, tmpf, dwpf from alldata where station = %s 
      and tmpf is not null and dwpf is not null 
      and valid > '1971-01-01' ORDER by valid ASC 
    """, (station,))
    
    hits = {}
    running = False
    startr = None
    for row in cursor:
        relh = met.relh( temperature(row[2], 'F'), temperature(row[3], 'F')).value('%')
        if relh > 25 or row[1] < (25.0/1.15):
            if running:
                delta = (row[0] - startr).seconds
                if delta >= 60*60*1:
                    #print station, delta, row
                    hits[ row[0].strftime("%Y%m%d")] = 1 
            running = False
        else:
            running = True
            startr = row[0]
    
    return len(hits.keys())
"""
data = {}
i = 0
for sid in nt.sts.keys():
    if nt.sts[sid]['archive_begin'] and nt.sts[sid]['archive_begin'].year < 1971:
        print sid, i, len(nt.sts.keys())
        data[sid] = get(sid)
    i += 1
print data
"""
data = {'FNT': 19, 'MIB': 136, 'FWA': 9, 'PAH': 4, 'GSH': 9, 'IOW': 12, 'PIA': 13, 'UIN': 20, 'SPI': 28, 'RAP': 479, 'BWG': 4, 'PIR': 222, 'SAW': 15, 'OFF': 36, 'BFF': 548, 'OFK': 218, 'IXD': 129, 'IAB': 116, 'LAN': 15, 'SYF': 371, 'PHG': 259, 'DAY': 13, 'FFO': 8, 'APN': 6, 'DBQ': 15, 
         'PHP': 206, 'SNY': 562, 'CMH': 14, 'DET': 11, 'GUS': 19, 'EMP': 147, 'CMX': 6, 'FDY': 7, 'MWC': 5, 'DTW': 28, 'EVV': 8, 'LSE': 14, 'MFD': 9, 'SZL': 43, 'JMS': 117, 'HUT': 106, 'HON': 95, 'OSC': 11, 'SUX': 127, 'CEY': 4, 'GRR': 17, 'GCK': 741, 'DLH': 15, 'BLM': 10, 'FOE': 85, 'DSM': 69, 'GRB': 5, 'SGF': 24, 'RFD': 25, 'DDC': 722, 'FTK': 3, 'GRI': 178, 'RWF': 63, 'CBK': 371, 'HTL': 5, 'SLN': 180, 'ANJ': 0, 'MOT': 118, 'INL': 5, 'ANW': 49, 'TBN': 21, 'IND': 11, 'BTL': 6, 'HLC': 299, 'LCK': 0, 'CZD': 3, 'DVL': 43, 'FSD': 88, 'ILN': 6, 'AKR': 2, 'GLD': 525, 'ISN': 190, 'ATY': 65, 'IKW': 14, 'ZZV': 3, 'LNR': 13, 'LNK': 138, 'JXN': 7, 'TVC': 3, 
          'CLE': 6, 'FRI': 73, 'LBF': 195, 'IML': 147, 'VTN': 277, 'YIP': 21, 'NRN': 259, 'ALO': 48, 'OMA': 78, 'TDZ': 13, 'BRL': 14, 'CDR': 447, 'LEX': 8, 'PLN': 7, 'ORD': 21, 'SBN': 18, 'MKG': 8, 'MKE': 32, 'MKC': 31, 'DIK': 200, 'TOP': 61, 'YNG': 6, 'MSP': 34, 'CAK': 7, 'MSN': 16, 'TOL': 18, 'LOZ': 4, 'CVG': 13, 'VOK': 5, 'BAK': 24, 'CAD': 2, 'ONL': 17, 'FAR': 111, 'RCA': 287, 'SGH': 3, 'EAR': 74, 'EAU': 7, 'BIS': 151, 'MBS': 22, 'CNU': 60, 'STC': 21, 'STL': 34, 'MLI': 21, 'STJ': 60, 'MCW': 83, 'ABR': 93, 'IRK': 24, 'ESC': 0, 'HOP': 7, 'MTC': 8, 'CNK': 157, 'ICT': 209, 'RSL': 402, 'OTM': 96, 'GFK': 71, 'SDF': 12, 'RST': 51}

lats = []
lons = []
vals = []
for sid in data.keys():
    lats.append( nt.sts[sid]['lat'] )
    lons.append( nt.sts[sid]['lon'] )
    vals.append( data[sid] / float(2013-1970.))
    
from pyiem.plot import MapPlot

m = MapPlot(sector='midwest', title='1971-2013 Days per Year with 1+ Hour >=25 mph & <25% RH')
m.plot_values(lons, lats, vals, '%.1f', textsize=18)

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')