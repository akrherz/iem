import psycopg2
pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor()

for mdl in ['cgcm3_t47', 'cgcm3_t63', 'cnrm', 'echam5', 'echo',
            'giss_aom', 'hadcm3', 'hadgem', 'miroc_hi', 'pcm']:
    sql = """
    WITH obs as (
     SELECT avg((f2c(high)+f2c(low))/2.) as avgt, sum(precip) from alldata_ia where
     station = 'IA0200' and year = 2012),
    
    forecast as (
     SELECT avg((f2c(high)+f2c(low))/2.) as avgt, sum(precip) from hayhoe_daily WHERE
     model = %s and scenario = 'a1b' and station = 'IA0200' and
     day between '2012-01-01' and '2013-01-01' and precip is not null and
     high is not null and low is not null)
     
    SELECT obs.avgt, obs.sum, forecast.avgt - obs.avgt, (forecast.sum - obs.sum) / 1. 
    from obs, forecast
    """
    cursor.execute(sql, (mdl,))
    row = cursor.fetchone()
    print "%10s %s %s %s %s" % (mdl, row[0], row[1], row[2], row[3])

"""
   WITH periods as (
   SELECT extract(year from day) as year, max(case when low < 32 and extract(month from day) < 7
           then extract(doy from day) else 0 end),
    min(case when low < 32 and extract(month from day) > 7
           then extract(doy from day) else 366 end)
    from hayhoe_daily WHERE model = %s and scenario = 'a1b' and
    station = 'IA0200' GROUP by year),
    foo as (
       SELECT year, min - max as d from periods
    )

    SELECT avg(case when year between 1980 and 2000 then d else null end),
     avg(case when year between 2046 and 2066 then d else null end)
    from foo

  with one as (
  SELECT sum(precip), avg((f2c(high)+f2c(low))/2.) as avgt,
  sum(case when high >= 100 then 1 else 0 end) as d100
  from hayhoe_daily where station = 'IA0200' and
  model = %s and scenario = 'a1b' and day between '1980-01-01' and '2000-01-01'),
  two as (
  SELECT sum(precip), avg((f2c(high)+f2c(low))/2.) as avgt,
  sum(case when high >= 100 then 1 else 0 end) as d100
  from hayhoe_daily where station = 'IA0200' and
  model = %s and scenario = 'a1b' and day between '2046-01-01' and '2066-01-01'
  )
  
  SELECT two.sum, one.sum, (two.sum - one.sum) / 20., one.d100, two.d100, one.avgt, two.avgt from one, two

"""