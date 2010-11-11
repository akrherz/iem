"""
select year, min(date) from (select date, year, count(*) from (select extract(year from valid) as year, date(valid) as date, count(*), station from alldata where station in ('EST','SPW','MCW','MIW','ALO','AMW','DSM','SUX','DSM','IOW','CID','DBQ','OTM','LWD','BRL') and metar ~* '-SN' and extract(month from valid) > 7 GROUP by year, station, date ORDER by date) as foo GROUP by date, year ORDER by date) as foo2 WHERE count >= 2 GROUP by year ORDER by year ASC
"""

data = """ 1948 | 1948-11-08
 1949 | 1949-11-20
 1950 | 1950-11-08
 1951 | 1951-11-03
 1952 | 1952-11-24
 1953 | 1953-11-20
 1954 | 1954-10-31
 1955 | 1955-10-30
 1956 | 1956-11-15
 1957 | 1957-10-24
 1958 | 1958-11-17
 1959 | 1959-10-27
 1960 | 1960-11-09
 1961 | 1961-11-02
 1962 | 1962-10-24
 1963 | 1963-11-22
 1964 | 1964-11-19
 1965 | 1965-11-18
 1966 | 1966-11-09
 1967 | 1967-10-26
 1968 | 1968-11-07
 1969 | 1969-11-18
 1970 | 1970-11-02
 1971 | 1971-11-08
 1972 | 1972-10-18
 1973 | 1973-11-04
 1974 | 1974-11-05
 1975 | 1975-11-12
 1976 | 1976-10-18
 1977 | 1977-11-09
 1978 | 1978-11-12
 1979 | 1979-10-22
 1980 | 1980-10-27
 1981 | 1981-10-23
 1982 | 1982-10-19
 1983 | 1983-11-12
 1984 | 1984-11-10
 1985 | 1985-11-08
 1986 | 1986-11-10
 1987 | 1987-10-10
 1988 | 1988-11-05
 1989 | 1989-10-30
 1990 | 1990-10-17
 1991 | 1991-10-05
 1992 | 1992-11-02
 1993 | 1993-10-29
 1994 | 1994-11-19
 1995 | 1995-10-23
 1996 | 1996-10-22
 1997 | 1997-10-26
 1998 | 1998-11-07
 1999 | 1999-10-01
 2000 | 2000-11-07
 2001 | 2001-10-24
 2002 | 2002-10-16
 2003 | 2003-10-29
 2004 | 2004-11-27
 2005 | 2005-10-23
 2006 | 2006-10-11
 2007 | 2007-11-05
 2008 | 2008-10-18
 2009 | 2009-10-10
 2010 | 2010-10-27"""

cdata = """ 1948 | 1948-11-07
 1949 | 1949-11-16
 1950 | 1950-11-02
 1951 | 1951-10-18
 1952 | 1952-10-17
 1953 | 1953-11-20
 1954 | 1954-10-29
 1955 | 1955-10-06
 1956 | 1956-11-07
 1957 | 1957-11-04
 1958 | 1958-11-17
 1959 | 1959-10-08
 1960 | 1960-10-21
 1961 | 1961-09-30
 1962 | 1962-10-24
 1963 | 1963-11-22
 1964 | 1964-11-12
 1965 | 1965-11-11
 1966 | 1966-10-14
 1967 | 1967-10-26
 1968 | 1968-11-08
 1969 | 1969-10-12
 1970 | 1970-10-09
 1971 | 1971-11-08
 1972 | 1972-10-16
 1973 | 1973-11-04
 1974 | 1974-11-05
 1975 | 1975-11-09
 1976 | 1976-10-18
 1977 | 1977-10-10
 1978 | 1978-11-11
 1979 | 1979-10-22
 1980 | 1980-10-26
 1981 | 1981-10-24
 1982 | 1982-10-19
 1983 | 1983-10-12
 1984 | 1984-10-17
 1985 | 1985-09-29
 1986 | 1986-10-13
 1987 | 1987-10-10
 1988 | 1988-11-05
 1989 | 1989-10-30
 1990 | 1990-10-17
 1991 | 1991-10-06
 1992 | 1992-10-20
 1993 | 1993-10-30
 1994 | 1994-11-04
 1995 | 1995-10-23
 1996 | 1996-10-22
 1997 | 1997-10-25
 1998 | 1998-11-07
 1999 | 1999-10-01
 2000 | 2000-11-07
 2001 | 2001-11-25
 2002 | 2002-10-16
 2003 | 2003-10-26
 2004 | 2004-11-24
 2005 | 2005-10-22
 2006 | 2006-10-11
 2007 | 2007-11-05
 2008 | 2008-10-21
 2009 | 2009-10-09
 2010 | 2010-10-27"""

import mx.DateTime

years = []
doy = []
for line in data.split("\n"):
	years.append( int(line.split("|")[0]) )
	doy.append( int(mx.DateTime.strptime((line.split("|")[1]).strip(), '%Y-%m-%d').strftime("%j")))

cyears = []
cdoy = []
for line in cdata.split("\n"):
	cyears.append( int(line.split("|")[0]) )
	cdoy.append( int(mx.DateTime.strptime((line.split("|")[1]).strip(), '%Y-%m-%d').strftime("%j")))

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter( years, doy, c='#ff0000', label='Airport Ob' )
ax.scatter( cyears, cdoy, c='r', marker="+", label='COOP Ob')
a = sum(doy)/float(len(doy))
ax.plot( (1948,2010), (a,a) , label='Average')
yticks = []
yticklabels = []
for mo in (9,10,11,12):
  for dy in (1, 15):
    ts = mx.DateTime.DateTime(2000,mo,dy)
    yticks.append( int(ts.strftime("%j")) )
    yticklabels.append( ts.strftime("%b %d") )
ax.set_yticks( yticks )
ax.set_yticklabels( yticklabels )
ax.set_xlim(1947.5,2010.5)
ax.set_xlabel('Year')
ax.set_ylabel('Day of the Year')
ax.set_title('Iowa\'s First Fall Season Report of Snow (1948-2010)')
ax.grid(True)
ax.legend(ncol=3)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
