import iemdb 
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
import network
import re
acursor.execute("SET TIME ZONE 'GMT'")

nt = network.Table('IA_ASOS')

out = open('asos_gusts.txt', 'w')
for id in nt.sts.keys():
	acursor.execute("""
select valid, metar, sknt, gust from alldata where station = %s and (metar ~* 'PK WND' or gust >= 50 or sknt >= 50)
	""", (id,))
	for row in acursor:
		ts = row[0]
		if row[2] >= 50 or row[3] >= 50:
			out.write("%s,%s,%s,%s,%s,%s\n" % (id, row[0], row[2], row[3], 0, row[1]))
		tokens = re.findall('PK WND [0-9]{3}([0-9]{2,3})/([0-9]{4})', row[1])
		if len(tokens) == 0:
			continue
		sknt = int(tokens[0][0])
		hr = int(tokens[0][1][:2])
		mi = int(tokens[0][1][2:])
		print tokens, row[1]
		if sknt >= 50:
			out.write("%s,%s,%s,%s,%s,%s\n" % (id, row[0], row[2], row[3], sknt, row[1]))

out.close()
