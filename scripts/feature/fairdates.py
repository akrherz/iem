sts = None
for line in open('/tmp/fair.txt'):
  tokens = line.split()
  if len(tokens) == 1:
    year = tokens[0]
  elif len(tokens) == 2:
    month = tokens[0]
    day = tokens[1]
    if sts is None:
      smonth = month
      sday = day
      sts = 1

  if len(tokens) == 0 and sts is not None:
    print '[mx.DateTime.DateTime(%s,%s,%s),mx.DateTime.DateTime(%s,%s,%s)],' % (year, smonth, sday, year, month, day)
    sts = None
