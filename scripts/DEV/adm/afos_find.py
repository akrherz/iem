from pyiem.network import Table as NetworkTable
import psycopg2
import datetime
from pyiem.nws.product import TextProduct

pgconn = psycopg2.connect(database='afos', host='iemdb', user='nobody')
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

nt = NetworkTable("WFO")


def findp(arr):
    place = 0
    for _, a in enumerate(arr):
        if place == 2:
            return a.replace("/", "")
        if a == '/':
            place += 1


def mycmp(orig, mod, data, data2, line, line2):
    p1 = findp(orig)
    p2 = findp(mod)
    if p1 == 'T' and p2 == 'M':
        tp = TextProduct(data)
        tp2 = TextProduct(data2)
        print(("%s %s -> %s\n"
               "%s -> %s\nhttps://mesonet.agron.iastate.edu/p.php?pid=%s\n"
               "%s -> %s\nhttps://mesonet.agron.iastate.edu/p.php?pid=%s\n") % (
            orig[0], p1, p2, tp.afos, line, tp.get_product_id(),
            tp2.afos, line2, tp2.get_product_id()))

for sid in nt.sts.keys():
    state = nt.sts[sid]['state']
    # Search for RTPs
    cursor.execute("""SELECT entered, data from products_2015_0712
    WHERE pil = %s and extract(hour from entered) between 5 and 10
    ORDER by entered""", ("RTP"+sid, ))
    for row in cursor:
        data = row[1]
        for line in data.split("\n"):
            tokens = line.strip().split()
            if len(tokens) > 3 and len(tokens[0]) == 3:
                if 'T' in tokens:
                    sts = row[0].replace(hour=5, minute=0)
                    ets = sts + datetime.timedelta(hours=5)
                    cursor2.execute("""SELECT entered, data from
                    products_2015_0712 WHERE entered > %s and entered < %s
                    and pil = %s""", (sts, ets, "RTP"+state))
                    for row2 in cursor2:
                        for line2 in row2[1].split("\n"):
                            tokens2 = line2.strip().split()
                            if (len(tokens2) > 3 and tokens2[0] == tokens[0]):
                                mycmp(tokens, tokens2, row[1], row2[1],
                                      line.strip(), line2.strip())
