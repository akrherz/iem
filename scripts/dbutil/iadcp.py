import iemdb
mesosite = iemdb.connect('mesosite')
mcursor = mesosite.cursor()
iem = iemdb.connect('iem')
icursor = iem.cursor()

for line in open('iadcp_adjust.txt').readlines()[1:]:
    tokens = line.split(",")
    # NWSLI:,Site Name:,,DCP only
    nwsli = tokens[0]
    better = tokens[2]
    dcponly = ''
    if len(tokens) == 4:
      dcponly = tokens[3].strip()
    if better != '':
      print '%s has better name of %s' % (nwsli, better)
      mcursor.execute("""
      UPDATE stations SET name = '%s' where id = '%s'
      """ % (better, nwsli))
      icursor.execute("""
      UPDATE current SET sname = '%s' where station = '%s'
      """ % (better, nwsli))
    if dcponly == 'X':
      print 'Deleting %s from IA_COOP' % (nwsli,)
      mcursor.execute("""
      DELETE from stations where id = '%s' and network = 'IA_COOP'
      """ % (nwsli))
      icursor.execute("""
      DELETE from current where station = '%s' and network = 'IA_COOP'
      """ % (nwsli))
      icursor.execute("""
      DELETE from summary where station = '%s' and network = 'IA_COOP'
      """ % (nwsli))

mcursor.close()
mesosite.commit()
mesosite.close()     
icursor.close()
iem.commit()
iem.close()     
