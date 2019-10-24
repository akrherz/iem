"""Simple helper script to generate schema"""
import datetime

for year in range(1929, 1996):
    print("""
    insert into alldata_save_github212 select a.* from t%(y)s a JOIN stations t ON (a.station = t.id)
where extract(day from valid at time zone 'UTC') = 1 and
extract(hour from valid at time zone 'UTC') >= 0 and
extract(day from valid at time zone tzname) > 12 and valid < '1996-01-01';

delete from t%(y)s a USING stations t where  a.station = t.id and
extract(day from valid at time zone 'UTC') = 1 and
extract(hour from valid at time zone 'UTC') >= 0 and
extract(day from valid at time zone tzname) > 12 and valid < '1996-01-01';
    """ % dict(y=year, y2=(year + 1)))
