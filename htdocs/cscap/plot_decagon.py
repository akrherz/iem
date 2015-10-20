#!/usr/bin/env python
"""Decagon SM Plot!"""
import psycopg2
import matplotlib
import sys
import cStringIO
import pandas as pd
from pandas.io.sql import read_sql
import cgi
import datetime
import pytz
import os
matplotlib.use('agg')
import matplotlib.pyplot as plt  # NOPEP8
import matplotlib.dates as mdates  # NOPEP8

DEPTHS = [None, '10 cm', '20 cm', '40 cm', '60 cm', '100 cm']

LINESTYLE = ['-', '-', '-', '-', '-', '-',
             '-', '-', '-.', '-.', '-.', '-.', '-.',
             '-', '-.', '-.', '-.', '-.', '-.']


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
    if uniqueid == 'MASON':
        DEPTHS[1] = None
        DEPTHS[5] = '80 cm'

    sts = datetime.datetime.strptime(form.getfirst('date', '2014-01-01'),
                                     '%Y-%m-%d')
    days = int(form.getfirst('days', 1))
    ets = sts + datetime.timedelta(days=days)
    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb')
    tzname = 'America/Chicago' if uniqueid in ['ISUAG', 'SERF', 'GILMORE'] else 'America/New_York'
    tz = pytz.timezone(tzname)
    viewopt = form.getfirst('view', 'plot')
    ptype = form.getfirst('ptype', '1')
    plotid_limit = "and plotid = '%s'" % (plotid, )
    depth = form.getfirst('depth', 'all')
    if depth != 'all':
        plotid_limit = ""
    if ptype == '1':
        df = read_sql("""SELECT valid at time zone 'UTC' as v, plotid,
        d1temp_qc as d1t, coalesce(d1temp_flag, '') as d1t_f,
        d2temp_qc as d2t, coalesce(d2temp_flag, '') as d2t_f,
        d3temp_qc as d3t, coalesce(d3temp_flag, '') as d3t_f,
        d4temp_qc as d4t, coalesce(d4temp_flag, '') as d4t_f,
        d5temp_qc as d5t, coalesce(d5temp_flag, '') as d5t_f,
        d1moisture_qc as d1m, coalesce(d1moisture_flag, '') as d1m_f,
        d2moisture_qc as d2m, coalesce(d2moisture_flag, '') as d2m_f,
        d3moisture_qc as d3m, coalesce(d3moisture_flag, '') as d3m_f,
        d4moisture_qc as d4m, coalesce(d4moisture_flag, '') as d4m_f,
        d5moisture_qc as d5m, coalesce(d5moisture_flag, '') as d5m_f
        from decagon_data WHERE uniqueid = %s """+plotid_limit+"""
        and valid between %s and %s ORDER by valid ASC
        """, pgconn, params=(uniqueid, sts.date(), ets.date()))
    elif ptype in ['3', '4']:
        res = 'hour' if ptype == '3' else 'week'
        df = read_sql("""SELECT
        date_trunc('"""+res+"""', valid at time zone 'UTC') as v, plotid,
        avg(d1temp_qc) as d1t, avg(d2temp_qc) as d2t,
        avg(d3temp_qc) as d3t, avg(d4temp_qc) as d4t, avg(d5temp_qc) as d5t,
        avg(d1moisture_qc) as d1m, avg(d2moisture_qc) as d2m,
        avg(d3moisture_qc) as d3m, avg(d4moisture_qc) as d4m,
        avg(d5moisture_qc) as d5m
        from decagon_data WHERE uniqueid = %s """+plotid_limit+"""
        and valid between %s and %s GROUP by v, plotid ORDER by v ASC
        """, pgconn, params=(uniqueid, sts.date(), ets.date()))
        for n in ['m', 't']:
            for i in range(1, 6):
                df["d%s%s_f" % (n, i)] = '-'
    else:
        df = read_sql("""SELECT date(valid at time zone %s) as v, plotid,
        avg(d1temp_qc) as d1t, avg(d2temp_qc) as d2t,
        avg(d3temp_qc) as d3t, avg(d4temp_qc) as d4t, avg(d5temp_qc) as d5t,
        avg(d1moisture_qc) as d1m, avg(d2moisture_qc) as d2m,
        avg(d3moisture_qc) as d3m, avg(d4moisture_qc) as d4m,
        avg(d5moisture_qc) as d5m
        from decagon_data WHERE uniqueid = %s  """+plotid_limit+"""
        and valid between %s and %s GROUP by v, plotid ORDER by v ASC
        """, pgconn, params=(tzname, uniqueid, sts.date(), ets.date()))
        for n in ['m', 't']:
            for i in range(1, 6):
                df["d%s%s_f" % (n, i)] = '-'
    if len(df.index) < 3:
        send_error("No / Not Enough Data Found, sorry!")
    if ptype not in ['2', ]:
        df['v'] = df['v'].apply(
            lambda x: x.tz_localize('UTC').tz_convert(tzname))

    if viewopt != 'plot':
        df.rename(columns=dict(v='timestamp',
                               d1t='%s Temp (C)' % (DEPTHS[1], ),
                               d2t='%s Temp (C)' % (DEPTHS[2], ),
                               d3t='%s Temp (C)' % (DEPTHS[3], ),
                               d4t='%s Temp (C)' % (DEPTHS[4], ),
                               d5t='%s Temp (C)' % (DEPTHS[5], ),
                               d1m='%s Moisture (cm3/cm3)' % (DEPTHS[1], ),
                               d2m='%s Moisture (cm3/cm3)' % (DEPTHS[2], ),
                               d3m='%s Moisture (cm3/cm3)' % (DEPTHS[3], ),
                               d4m='%s Moisture (cm3/cm3)' % (DEPTHS[4], ),
                               d5m='%s Moisture (cm3/cm3)' % (DEPTHS[5], ),
                               d1t_f='%s Temp Flag' % (DEPTHS[1], ),
                               d2t_f='%s Temp Flag' % (DEPTHS[2], ),
                               d3t_f='%s Temp Flag' % (DEPTHS[3], ),
                               d4t_f='%s Temp Flag' % (DEPTHS[4], ),
                               d5t_f='%s Temp Flag' % (DEPTHS[5], ),
                               d1m_f='%s Moisture Flag' % (DEPTHS[1], ),
                               d2m_f='%s Moisture Flag' % (DEPTHS[2], ),
                               d3m_f='%s Moisture Flag' % (DEPTHS[3], ),
                               d4m_f='%s Moisture Flag' % (DEPTHS[4], ),
                               d5m_f='%s Moisture Flag' % (DEPTHS[5], ),
                               ),
                  inplace=True)
        if viewopt == 'html':
            sys.stdout.write("Content-type: text/html\n\n")
            sys.stdout.write(df.to_html(index=False))
            return
        if viewopt == 'csv':
            sys.stdout.write('Content-type: application/octet-stream\n')
            sys.stdout.write(('Content-Disposition: attachment; '
                              'filename=%s_%s_%s_%s.csv\n\n'
                              ) % (uniqueid, plotid, sts.strftime("%Y%m%d"),
                                   ets.strftime("%Y%m%d")))
            sys.stdout.write(df.to_csv(index=False))
            return
        if viewopt == 'excel':
            sys.stdout.write('Content-type: application/octet-stream\n')
            sys.stdout.write(('Content-Disposition: attachment; '
                              'filename=%s_%s_%s_%s.xlsx\n\n'
                              ) % (uniqueid, plotid, sts.strftime("%Y%m%d"),
                                   ets.strftime("%Y%m%d")))
            writer = pd.ExcelWriter('/tmp/ss.xlsx')
            df.to_excel(writer, 'Data', index=False)
            writer.save()
            sys.stdout.write(open('/tmp/ss.xlsx', 'rb').read())
            os.unlink('/tmp/ss.xlsx')
            return

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    lbl = "Plot:%s" % (plotid,)
    if depth != 'all':
        lbl = "Depth:%s" % (DEPTHS[int(depth)],)
    ax[0].set_title(("Decagon Temperature + Moisture for\n"
                     "Site:%s %s Period:%s to %s"
                     ) % (uniqueid, lbl, sts.date(), ets.date()))
    if depth == 'all':
        ax[0].plot(df['v'], df['d1t'].astype('f'), c='r', lw=2,
                   label=DEPTHS[1])
        ax[0].plot(df['v'], df['d2t'].astype('f'), c='purple', lw=2,
                   label=DEPTHS[2])
        ax[0].plot(df['v'], df['d3t'].astype('f'), c='b', lw=2,
                   label=DEPTHS[3])
        ax[0].plot(df['v'], df['d4t'].astype('f'), c='g', lw=2,
                   label=DEPTHS[4])
        ax[0].plot(df['v'], df['d5t'].astype('f'), c='turquoise', lw=2,
                   label=DEPTHS[5])
        lines = 5
    else:
        dlevel = "d%st" % (depth, )
        for i, plotid in enumerate(df['plotid'].unique()):
            df2 = df[df['plotid'] == plotid]
            ax[0].plot(df2['v'], df2[dlevel].astype('f'), lw=2,
                       label=plotid, linestyle=LINESTYLE[i])
        lines = len(df['plotid'].unique())

    ax[0].grid()
    ax[0].set_ylabel("Temperature [C]")
    if lines < 7:
        ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, 0), ncol=6,
                     fontsize=12)
    else:
        ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, 0), ncol=6,
                     fontsize=8)
    if depth == 'all':
        ax[1].plot(df['v'], df['d1m'].astype('f'), c='r', lw=2)
        ax[1].plot(df['v'], df['d2m'].astype('f'), c='purple', lw=2)
        ax[1].plot(df['v'], df['d3m'].astype('f'), c='b', lw=2)
        ax[1].plot(df['v'], df['d4m'].astype('f'), c='g', lw=2)
        ax[1].plot(df['v'], df['d5m'].astype('f'), c='turquoise', lw=2)
        v = min([df['d1m'].min(), df['d2m'].min(), df['d3m'].min(),
                 df['d4m'].min(), df['d5m'].min()])
        v2 = max([df['d1m'].max(), df['d2m'].max(), df['d3m'].max(),
                  df['d4m'].max(), df['d5m'].max()])
        #ax[1].set_ylim(0 if v > 0 else v, v2 + v2 * 0.05)
    else:
        dlevel = "d%sm" % (depth, )
        for plotid in df['plotid'].unique():
            df2 = df[df['plotid'] == plotid]
            ax[1].plot(df2['v'], df2[dlevel].astype('f'), lw=2)
    ax[1].grid(True)
    ax[1].set_ylabel("Volumetric Soil Moisture [cm$^{3}$ cm$^{-3}$]",
                     fontsize=9)
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
