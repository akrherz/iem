#!/usr/bin/env python
"""Plot!"""
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

LINESTYLE = ['-', '-', '-', '-', '-', '-',
             '-', '-', '-.', '-.', '-.', '-.', '-.',
             '-', '-.', '-.', '-.', '-.', '-.', '-.', '-.', '-.', '-.', '-.']


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
    tzname = 'America/Chicago' if uniqueid in [
        'ISUAG', 'SERF', 'GILMORE'] else 'America/New_York'
    tz = pytz.timezone(tzname)
    viewopt = form.getfirst('view', 'plot')
    ptype = form.getfirst('ptype', '1')
    plotid_limit = "and plotid = '%s'" % (plotid, )
    if ptype == '1':
        df = read_sql("""SELECT valid at time zone 'UTC' as v, plotid,
        depth_mm_qc as depth, coalesce(depth_mm_qcflag, '') as depth_f
        from watertable_data WHERE uniqueid = %s
        and valid between %s and %s ORDER by valid ASC
        """, pgconn, params=(uniqueid, sts.date(), ets.date()))
    elif ptype in ['3', '4']:
        res = 'hour' if ptype == '3' else 'week'
        df = read_sql("""SELECT
        date_trunc('"""+res+"""', valid at time zone 'UTC') as v, plotid,
        avg(depth_mm_qc) as depth
        from watertable_data WHERE uniqueid = %s
        and valid between %s and %s GROUP by v, plotid ORDER by v ASC
        """, pgconn, params=(uniqueid, sts.date(), ets.date()))
        df["depth_f"] = '-'
    else:
        df = read_sql("""SELECT date(valid at time zone %s) as v, plotid,
        avg(depth_mm_qc) as depth
        from watertable_data WHERE uniqueid = %s
        and valid between %s and %s GROUP by v, plotid ORDER by v ASC
        """, pgconn, params=(tzname, uniqueid, sts.date(), ets.date()))
        df["depth_f"] = '-'
    if len(df.index) < 3:
        send_error("No / Not Enough Data Found, sorry!")
    if ptype not in ['2', ]:
        df['v'] = df['v'].apply(
            lambda x: x.tz_localize('UTC').tz_convert(tzname))

    if viewopt != 'plot':
        df.rename(columns=dict(v='timestamp',
                               depth='Depth (mm)'
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

    (fig, ax) = plt.subplots(1, 1, sharex=True)
    ax.set_title(("Water Table Depth for\n"
                  "Site:%s Period:%s to %s"
                  ) % (uniqueid, sts.date(), ets.date()))
    plot_ids = df['plotid'].unique()
    plot_ids.sort()
    for i, plotid in enumerate(plot_ids):
        df2 = df[df['plotid'] == plotid]
        ax.plot(df2['v'], df2['depth'].astype('f'), lw=2,
                label=plotid, linestyle=LINESTYLE[i])
    lines = len(df['plotid'].unique())

    ax.grid()
    ax.set_ylabel("Depth [mm]")
    box = ax.get_position()
    ax.set_position((box.x0, 0.15, box.width, 0.75))
    if lines < 7:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=6,
                  fontsize=12)
    else:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=6,
                  fontsize=8)
    yrange = ax.get_ylim()
    ax.set_ylim(yrange[1], 0)
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
