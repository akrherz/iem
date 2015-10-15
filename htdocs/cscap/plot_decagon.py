#!/usr/bin/env python
"""Decagon SM Plot!"""
import psycopg2
import matplotlib
import sys
import cStringIO
from pandas.io.sql import read_sql
import cgi
import datetime
import pytz
matplotlib.use('agg')
import matplotlib.pyplot as plt  # NOPEP8
import matplotlib.dates as mdates  # NOPEP8


def send_error(msg):
    """" """
    fig, ax = plt.subplots(1, 1)
    ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha='center')
    sys.stdout.write("Content-type: image/png\n\n")
    ram = cStringIO.StringIO()
    fig.savefig(ram, format='png')
    ram.seek(0)
    sys.stdout.write(ram.read())
    sys.exit()


def make_plot(form):
    """Make the plot"""
    (uniqueid, plotid) = form.getfirst('site', 'ISUAG::302E').split("::")

    sts = datetime.datetime.strptime(form.getfirst('date', '2014-01-01'),
                                     '%Y-%m-%d')
    days = int(form.getfirst('days', 1))
    ets = sts + datetime.timedelta(days=days)
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
    tzname = 'America/Chicago' if uniqueid in ['ISUAG', 'SERF', 'GILMORE'] else 'America/New_York'
    tz = pytz.timezone(tzname)
    ptype = form.getfirst('ptype', '1')
    if ptype == '1':
        df = read_sql("""SELECT valid at time zone 'UTC' as v,
        d1temp as d1t, d2temp as d2t, d3temp as d3t, d4temp as d4t,
        d5temp as d5t,
        d1moisture as d1m, d2moisture as d2m, d3moisture as d3m,
        d4moisture as d4m, d5moisture as d5m
        from decagon_data WHERE uniqueid = %s and plotid = %s
        and valid between %s and %s ORDER by valid ASC
        """, pgconn, params=(uniqueid, plotid, sts.date(), ets.date()))
    else:
        df = read_sql("""SELECT date(valid) as v,
        avg(d1temp) as d1t, avg(d2temp) as d2t,
        avg(d3temp) as d3t, avg(d4temp) as d4t, avg(d5temp) as d5t,
        avg(d1moisture) as d1m, avg(d2moisture) as d2m,
        avg(d3moisture) as d3m, avg(d4moisture) as d4m,
        avg(d5moisture) as d5m
        from decagon_data WHERE uniqueid = %s and plotid = %s
        and valid between %s and %s GROUP by v ORDER by v ASC
        """, pgconn, params=(uniqueid, plotid, sts.date(), ets.date()))
    if len(df.index) < 3:
        send_error("No Data Found, sorry!")

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    ax[0].set_title(("Decagon Temperature + Moisture for\n%s %s %s -> %s"
                     ) % (uniqueid, plotid, sts.date(), ets.date()))
    ax[0].plot(df['v'], df['d1t'], lw=2, label='10cm')
    ax[0].plot(df['v'], df['d2t'], lw=2, label='20cm')
    ax[0].plot(df['v'], df['d3t'], lw=2, label='40cm')
    ax[0].plot(df['v'], df['d4t'], lw=2, label='60cm')
    ax[0].plot(df['v'], df['d5t'], lw=2, label='100cm')
    ax[0].grid()
    ax[0].set_ylabel("Temperature [C]")
    ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.001), ncol=5,
                 fontsize=12)

    ax[1].plot(df['v'], df['d1m'], lw=2)
    ax[1].plot(df['v'], df['d2m'], lw=2)
    ax[1].plot(df['v'], df['d3m'], lw=2)
    ax[1].plot(df['v'], df['d4m'], lw=2)
    ax[1].plot(df['v'], df['d5m'], lw=2)
    ax[1].grid(True)
    ax[1].set_ylabel("Volumetric Soil Moisture [%]", fontsize=9)
    if days > 4:
        ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y',
                                                             tz=tz))
    else:
        ax[1].xaxis.set_major_formatter(
            mdates.DateFormatter('%I %p\n%-d %b', tz=tz))
    sys.stdout.write("Content-type: image/png\n\n")
    ram = cStringIO.StringIO()
    fig.savefig(ram, format='png')
    ram.seek(0)
    sys.stdout.write(ram.read())


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    make_plot(form)

if __name__ == '__main__':
    main()
