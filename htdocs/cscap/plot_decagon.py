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
    viewopt = form.getfirst('view', 'plot')
    ptype = form.getfirst('ptype', '1')
    if ptype == '1':
        df = read_sql("""SELECT valid at time zone 'UTC' as v,
        d1temp_qc as d1t, d2temp_qc as d2t, d3temp_qc as d3t, d4temp_qc as d4t,
        d5temp_qc as d5t,
        d1moisture_qc as d1m, d2moisture_qc as d2m, d3moisture_qc as d3m,
        d4moisture_qc as d4m, d5moisture_qc as d5m
        from decagon_data WHERE uniqueid = %s and plotid = %s
        and valid between %s and %s ORDER by valid ASC
        """, pgconn, params=(uniqueid, plotid, sts.date(), ets.date()))
    elif ptype == '3':
        df = read_sql("""SELECT date_trunc('hour', valid) as v,
        avg(d1temp_qc) as d1t, avg(d2temp_qc) as d2t,
        avg(d3temp_qc) as d3t, avg(d4temp_qc) as d4t, avg(d5temp_qc) as d5t,
        avg(d1moisture_qc) as d1m, avg(d2moisture_qc) as d2m,
        avg(d3moisture_qc) as d3m, avg(d4moisture_qc) as d4m,
        avg(d5moisture_qc) as d5m
        from decagon_data WHERE uniqueid = %s and plotid = %s
        and valid between %s and %s GROUP by v ORDER by v ASC
        """, pgconn, params=(uniqueid, plotid, sts.date(), ets.date()))
    else:
        df = read_sql("""SELECT date(valid at time zone %s) as v,
        avg(d1temp_qc) as d1t, avg(d2temp_qc) as d2t,
        avg(d3temp_qc) as d3t, avg(d4temp_qc) as d4t, avg(d5temp_qc) as d5t,
        avg(d1moisture_qc) as d1m, avg(d2moisture_qc) as d2m,
        avg(d3moisture_qc) as d3m, avg(d4moisture_qc) as d4m,
        avg(d5moisture_qc) as d5m
        from decagon_data WHERE uniqueid = %s and plotid = %s
        and valid between %s and %s GROUP by v ORDER by v ASC
        """, pgconn, params=(tzname, uniqueid, plotid, sts.date(), ets.date()))
    if len(df.index) < 3:
        send_error("No / Not Enough Data Found, sorry!")
    if ptype not in ['2', ]:
        df['v'] = df['v'].apply(
            lambda x: x.tz_localize('UTC').tz_convert(tzname))

    if viewopt != 'plot':
        df.rename(columns=dict(v='timestamp', d1t='Depth1 Temp (C)',
                               d2t='Depth2 Temp (C)', d3t='Depth3 Temp (C)',
                               d4t='Depth4 Temp (C)', d5t='Depth5 Temp (C)',
                               d1m='Depth1 Moisture (1)',
                               d2m='Depth2 Moisture (1)',
                               d3m='Depth3 Moisture (1)',
                               d4m='Depth4 Moisture (1)',
                               d5m='Depth5 Moisture (1)'),
                  inplace=True)
        if viewopt == 'html':
            sys.stdout.write("Content-type: text/html\n\n")
            sys.stdout.write(df.to_html(index=False))
            return
        if viewopt == 'csv':
            sys.stdout.write("Content-type: text/plain\n\n")
            sys.stdout.write(df.to_csv(index=False))
            return

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    ax[0].set_title(("Decagon Temperature + Moisture for\n"
                     "Site:%s Plot:%s Period:%s to %s"
                     ) % (uniqueid, plotid, sts.date(), ets.date()))
    ax[0].plot(df['v'], df['d1t'].astype('f'), c='r', lw=2, label='10cm')
    ax[0].plot(df['v'], df['d2t'].astype('f'), c='purple', lw=2, label='20cm')
    ax[0].plot(df['v'], df['d3t'].astype('f'), c='b', lw=2, label='40cm')
    ax[0].plot(df['v'], df['d4t'].astype('f'), c='g', lw=2, label='60cm')
    ax[0].plot(df['v'], df['d5t'].astype('f'), c='turquoise', lw=2,
               label='100cm')
    ax[0].grid()
    ax[0].set_ylabel("Temperature [C]")
    ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, 0), ncol=5,
                 fontsize=12)

    ax[1].plot(df['v'], df['d1m'].astype('f'), c='r', lw=2)
    ax[1].plot(df['v'], df['d2m'].astype('f'), c='purple', lw=2)
    ax[1].plot(df['v'], df['d3m'].astype('f'), c='b', lw=2)
    ax[1].plot(df['v'], df['d4m'].astype('f'), c='g', lw=2)
    ax[1].plot(df['v'], df['d5m'].astype('f'), c='turquoise', lw=2)
    ax[1].grid(True)
    v = min([df['d1m'].min(), df['d2m'].min(), df['d3m'].min(),
             df['d4m'].min(), df['d5m'].min()])
    v2 = max([df['d1m'].max(), df['d2m'].max(), df['d3m'].max(),
              df['d4m'].max(), df['d5m'].max()])
    ax[1].set_ylim(0 if v > 0 else v, v2 + v2 * 0.05)
    ax[1].set_ylabel("Volumetric Soil Moisture [1]", fontsize=9)
    if days > 4:
        ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y',
                                                             tz=tz))
    else:
        ax[1].xaxis.set_major_formatter(
            mdates.DateFormatter('%I %p\n%-d %b', tz=tz))
    ax[1].set_xlabel("Time (%s Timezone)" % (tzname, ))
    plt.subplots_adjust(bottom=0.15)
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
