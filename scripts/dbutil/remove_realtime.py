import iemdb, sys, mx.DateTime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
year = mx.DateTime.now().year

icursor.execute("""
 DELETE from current where iemid = (select iemid from stations where id = '%s' and network = '%s')
""" % (sys.argv[2],sys.argv[1]))

icursor.execute("""
 DELETE from summary_%s where iemid = (select iemid from stations where id = '%s' and network = '%s') and day in ('TODAY','TOMORROW')
""" % (year, sys.argv[2],sys.argv[1]))

icursor.close()
IEM.commit()

mcursor.execute("""
update stations SET online = false where id = '%s' and network = '%s'
""" % (sys.argv[2],sys.argv[1]))

mcursor.close()
MESOSITE.commit()
