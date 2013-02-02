import os, network
nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
 "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "KYCLIMATE", "ILCLIMATE", "WICLIMATE",
 "INCLIMATE", "OHCLIMATE", "MICLIMATE"))
PLOTS = ['annual_sum_precip', 'annual_avg_temp', 'frost_free',
   'gdd50', 'hdd65']
PLOTS = ['summer_avg_temp','fall_avg_temp', 'spring_avg_temp', 'winter_avg_temp']
PLOTS = ['summer_avg_high', 'winter_avg_low', 'summer_avg_low', 'winter_avg_low']
PLOTS = ['summer_avg_high','summer_avg_low']
#PLOTS = ['rain_days',]
for plot_type in PLOTS:
  for station in nt.sts.keys():
    #if station[2:] != '0000' and station[2] != 'C':
    if station != 'IA0000':
        continue
    first_year = 1951
    #if station[:3] in ['IAC',]:
    #    first_year = 1951
    #else:
    #    continue
    for format in ['eps', 'png']:
      fn = 'plots/%s_%s.%s' % (station, plot_type, format)
      url = 'http://iem.local/cgi-bin/climate/cplot.py?first_year=%s&station=%s&plot_type=%s&format=%s&linregress=on' % (
                                first_year, station, plot_type, format)
      cmd = 'wget -q -O %s "%s"' % (fn, url)
      os.system(cmd)
