#!/usr/bin/env python
""" Soil Moisture Timeseries """
import datetime
import numpy as np
import pytz
import sys
import pyiem.meteorology as meteorology
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable
import cgi
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt  # NOPEP8
import matplotlib.dates as mdates  # NOPEP8

ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
nt = NetworkTable("ISUSM")


def make_daily_pet_plot(station, sts, ets):
    """Generate a daily PET plot"""
    icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute("""WITH climo as (
        select to_char(valid, 'mmdd') as mmdd, avg(c70) as  et
        from daily where station = 'A130209' GROUP by mmdd
    ), obs as (
        SELECT valid, dailyet_qc / 25.4 as et, to_char(valid, 'mmdd') as mmdd
        from sm_daily WHERE station = '%s' and valid >= '%s' and valid <= '%s'
    )

    select o.valid, o.et, c.et from obs o
    JOIN climo c on (c.mmdd = o.mmdd) ORDER by o.valid ASC
    """ % (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
    dates = []
    o_dailyet = []
    c_et = []
    for row in icursor:
        dates.append(row[0])
        o_dailyet.append(row[1] if row[1] is not None else 0)
        c_et.append(row[2])

    (_, ax) = plt.subplots(1, 1)
    ax.bar(dates, o_dailyet, fc='brown', ec='brown', zorder=1,
           align='center', label='Observed')
    ax.plot(dates, c_et, label="Climatology", color='k', lw=1.5, zorder=2)
    ax.grid(True)
    ax.set_ylabel("Potential Evapotranspiration [inch]")
    ax.set_title(("ISUSM Station: %s Timeseries\n"
                  "Potential Evapotranspiration, "
                  "Climatology from Ames 1986-2014"
                  ) % (nt.sts[station]['name'], ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    interval = len(dates) / 7 + 1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.legend(loc='best', ncol=1, fontsize=10)
    sys.stdout.write("Content-Type: image/png\n\n")
    plt.savefig(sys.stdout, format='png')


def make_daily_rad_plot(station, sts, ets):
    """Generate a daily radiation plot"""
    # Get clear sky theory
    theory = meteorology.clearsky_shortwave_irradiance_year(
                nt.sts[station]['lat'],
                nt.sts[station]['elevation'])

    icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute("""SELECT valid, slrmj_tot_qc from sm_daily
    where station = '%s'
    and valid >= '%s' and valid <= '%s' and slrmj_tot_qc is not null
    ORDER by valid ASC
    """ % (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
    dates = []
    vals = []
    tmax = []
    for row in icursor:
        dates.append(row[0])
        vals.append(row[1])
        jday = int(row[0].strftime("%j"))
        if jday > 364:
            jday = 364
        tmax.append(theory[jday])

    (_, ax) = plt.subplots(1, 1)
    ax.bar(dates, vals, fc='tan', ec='brown', zorder=2,
           align='center', label='Observed')
    ax.plot(dates, tmax, label=r"Modelled Max $\tau$ =0.75", color='k', lw=1.5)
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    interval = len(dates) / 7 + 1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.set_ylabel("Solar Radiation $MJ m^{-2}$")
    ax.set_title(("ISUSM Station: %s Timeseries\n"
                  "Daily Solar Radiation"
                  ) % (nt.sts[station]['name'], ))
    ax.legend(loc='best', ncol=1, fontsize=10)
    sys.stdout.write("Content-Type: image/png\n\n")
    plt.savefig(sys.stdout, format='png')


def make_daily_plot(station, sts, ets):
    """Generate a daily plot of max/min 4 inch soil temps"""
    icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute("""SELECT date(valid), min(tsoil_c_avg_qc),
    max(tsoil_c_avg_qc), avg(tsoil_c_avg_qc) from sm_hourly
    where station = '%s' and valid >= '%s 00:00' and valid < '%s 23:56'
    and tsoil_c_avg is not null GROUP by date ORDER by date ASC
    """ % (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
    dates = []
    mins = []
    maxs = []
    avgs = []
    for row in icursor:
        dates.append(row[0])
        mins.append(row[1])
        maxs.append(row[2])
        avgs.append(row[3])

    mins = temperature(np.array(mins), 'C').value('F')
    maxs = temperature(np.array(maxs), 'C').value('F')
    avgs = temperature(np.array(avgs), 'C').value('F')
    (_, ax) = plt.subplots(1, 1)
    ax.bar(dates, maxs - mins, bottom=mins, fc='tan', ec='brown', zorder=2,
           align='center', label='Max/Min')
    ax.scatter(dates, avgs, marker='*', s=30, zorder=3, color='brown',
               label='Hourly Avg')
    ax.axhline(50, lw=1.5, c='k')
    ax.grid(True)
    ax.set_ylabel("4 inch Soil Temperature $^\circ$F")
    ax.set_title(("ISUSM Station: %s Timeseries\n"
                  "Daily Max/Min/Avg 4 inch Soil Temperatures"
                  ) % (nt.sts[station]['name'], ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))
    interval = len(dates) / 7 + 1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.legend(loc='best', ncol=2, fontsize=10)
    sys.stdout.write("Content-Type: image/png\n\n")
    plt.savefig(sys.stdout, format='png')


def main():

    # Query out the CGI variables
    form = cgi.FieldStorage()
    if ("year1" in form and "year2" in form and
            "month1" in form and "month2" in form and
            "day1" in form and "day2" in form and
            "hour1" in form and "hour2" in form):
        sts = datetime.datetime(int(form["year1"].value),
                                int(form["month1"].value),
                                int(form["day1"].value),
                                int(form["hour1"].value), 0)
        ets = datetime.datetime(int(form["year2"].value),
                                int(form["month2"].value),
                                int(form["day2"].value),
                                int(form["hour2"].value), 0)

    station = form.getvalue('station', 'CAMI4')
    opt = form.getvalue('opt', '1')
    if station not in nt.sts:
        print 'Content-type: text/plain\n'
        print 'ERROR'
        sys.exit(0)
    if opt == '3':
        make_daily_plot(station, sts, ets)
        return
    elif opt == '4':
        make_daily_rad_plot(station, sts, ets)
        return
    elif opt == '5':
        make_daily_pet_plot(station, sts, ets)
        return
    icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """SELECT * from sm_hourly WHERE
        station = '%s' and valid BETWEEN '%s' and '%s' ORDER by valid ASC
        """ % (station, sts.strftime("%Y-%m-%d %H:%M"),
               ets.strftime("%Y-%m-%d %H:%M"))
    icursor.execute(sql)
    d12sm = []
    d24sm = []
    d50sm = []
    d12t = []
    d24t = []
    d50t = []
    tair = []
    tsoil = []
    valid = []
    slrkw = []
    rain = []
    for row in icursor:
        slrkw.append(row['slrkw_avg_qc'] or np.nan)
        d12sm.append(row['vwc_12_avg_qc'] or np.nan)
        d12t.append(row['t12_c_avg_qc'] or np.nan)
        d24t.append(row['t24_c_avg_qc'] or np.nan)
        d50t.append(row['t50_c_avg_qc'] or np.nan)
        d24sm.append(row['vwc_24_avg_qc'] or np.nan)
        d50sm.append(row['vwc_50_avg_qc'] or np.nan)
        valid.append(row['valid'])
        rain.append(row['rain_mm_tot_qc'] or np.nan)
        tair.append(row['tair_c_avg_qc'] or np.nan)
        tsoil.append(row['tsoil_c_avg_qc'] or np.nan)

    slrkw = np.array(slrkw)
    rain = np.array(rain)
    d12sm = np.array(d12sm)
    d24sm = np.array(d24sm)
    d50sm = np.array(d50sm)
    d12t = np.array(d12t)
    d24t = np.array(d24t)
    d50t = np.array(d50t)
    tair = np.array(tair)
    tsoil = np.array(tsoil)

    # maxy = max([np.max(d12sm), np.max(d24sm), np.max(d50sm)])
    # miny = min([np.min(d12sm), np.min(d24sm), np.min(d50sm)])

    if opt == '2':
        (_, ax) = plt.subplots(1, 1)
        ax.grid(True)
        ax.set_title(("ISUSM Station: %s Timeseries\n"
                      "Soil Temperature at Depth\n "
                      ) % (nt.sts[station]['name'], ))
        ax.plot(valid, temperature(tsoil, 'C').value('F'), linewidth=2,
                color='brown', label='4 inch')
        ax.plot(valid, temperature(d12t, 'C').value('F'), linewidth=2,
                color='r', label='12 inch')
        ax.plot(valid, temperature(d24t, 'C').value('F'), linewidth=2,
                color='purple', label='24 inch')
        ax.plot(valid, temperature(d50t, 'C').value('F'), linewidth=2,
                color='black', label='50 inch')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width,
                        box.height * 0.9])
        ax.legend(bbox_to_anchor=(0.5, 1.02), ncol=4, loc='center',
                  fontsize=12)
        days = (ets - sts).days
        if days >= 3:
            interval = max(int(days/7), 1)
            ax.xaxis.set_major_locator(
                mdates.DayLocator(interval=interval,
                                  tz=pytz.timezone("America/Chicago")))
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter('%-d %b\n%Y',
                                     tz=pytz.timezone("America/Chicago")))
        else:
            ax.xaxis.set_major_locator(
                mdates.AutoDateLocator(maxticks=10,
                                       tz=pytz.timezone("America/Chicago")))
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter('%-I %p\n%d %b',
                                     tz=pytz.timezone("America/Chicago")))
        if ax.get_ylim()[0] < 40:
            ax.axhline(32, linestyle='--', lw=2, color='tan')
        ax.set_ylabel("Temperature $^\circ$F")
        sys.stdout.write("Content-Type: image/png\n\n")
        plt.savefig(sys.stdout, format='png')
        sys.exit()

    (_, ax) = plt.subplots(3, 1, sharex=True, figsize=(8, 8))
    ax[0].grid(True)
    ax2 = ax[0].twinx()
    ax[0].set_zorder(ax2.get_zorder()+1)
    ax[0].patch.set_visible(False)
    ax2.set_yticks(np.arange(-0.6, 0., 0.1))
    ax2.set_yticklabels(0 - np.arange(-0.6, 0.01, 0.1))
    ax2.set_ylim(-0.6, 0)
    ax2.set_ylabel("Hourly Precipitation [inch]")
    b1 = ax2.bar(valid, 0 - rain / 25.4, width=0.04, fc='b', ec='b', zorder=4)

    l1, = ax[0].plot(valid, d12sm * 100.0, linewidth=2, color='r', zorder=5)
    l2, = ax[0].plot(valid, d24sm * 100.0, linewidth=2, color='purple',
                     zorder=5)
    l3, = ax[0].plot(valid, d50sm * 100.0, linewidth=2, color='black',
                     zorder=5)
    ax[0].set_ylabel("Volumetric Soil Water Content [%]", fontsize=10)

    days = (ets - sts).days
    if days >= 3:
        interval = max(int(days/7), 1)
        ax[0].xaxis.set_major_locator(
            mdates.DayLocator(interval=interval,
                              tz=pytz.timezone("America/Chicago")))
        ax[0].xaxis.set_major_formatter(
            mdates.DateFormatter('%-d %b\n%Y',
                                 tz=pytz.timezone("America/Chicago")))
    else:
        ax[0].xaxis.set_major_locator(
            mdates.AutoDateLocator(maxticks=10,
                                   tz=pytz.timezone("America/Chicago")))
        ax[0].xaxis.set_major_formatter(
            mdates.DateFormatter('%-I %p\n%d %b',
                                 tz=pytz.timezone("America/Chicago")))

    ax[0].set_title(("ISUSM Station: %s Timeseries"
                     ) % (nt.sts[station]['name'], ))
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0 + box.height * 0.05, box.width,
                        box.height * 0.95])
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0 + box.height * 0.05, box.width,
                      box.height * 0.95])
    ax[0].legend([l1, l2, l3, b1],
                 ['12 inch', '24 inch', '50 inch', 'Hourly Precip'],
                 bbox_to_anchor=(0.5, -0.15), ncol=4, loc='center',
                 fontsize=12)

    # ----------------------------------------
    ax[1].plot(valid, temperature(d12t, 'C').value('F'), linewidth=2,
               color='r', label='12in')
    ax[1].plot(valid, temperature(d24t, 'C').value('F'), linewidth=2,
               color='purple', label='24in')
    ax[1].plot(valid, temperature(d50t, 'C').value('F'), linewidth=2,
               color='black', label='50in')
    ax[1].grid(True)
    ax[1].set_ylabel(r"Temperature $^\circ$F")
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0 + box.height * 0.05, box.width,
                        box.height * 0.95])

    # ------------------------------------------------------

    ax2 = ax[2].twinx()
    l3, = ax2.plot(valid, slrkw, color='g', zorder=1, lw=2)
    ax2.set_ylabel("Solar Radiation [W/m^2]", color='g')

    l1, = ax[2].plot(valid, temperature(tair, 'C').value('F'), linewidth=2,
                     color='blue', zorder=2)
    l2, = ax[2].plot(valid, temperature(tsoil, 'C').value('F'), linewidth=2,
                     color='brown', zorder=2)
    ax[2].grid(True)
    ax[2].legend([l1, l2, l3],
                 ['Air', '4" Soil', 'Solar Radiation'],
                 bbox_to_anchor=(0.5, 1.1), loc='center', ncol=3)
    ax[2].set_ylabel(r"Temperature $^\circ$F")

    ax[2].set_zorder(ax2.get_zorder()+1)
    ax[2].patch.set_visible(False)
    # Wow, strange bugs if I did not put this last
    ax[0].set_xlim(min(valid), max(valid))

    sys.stdout.write("Content-Type: image/png\n\n")
    plt.savefig(sys.stdout, format='png')

if __name__ == '__main__':
    main()
