import pandas as pd
import datetime
from collections import OrderedDict
from pyiem.meteorology import gdd
from pyiem.datatypes import temperature, distance

STATIONS = OrderedDict([
        ('ames', 'Central (Ames'),
        ('cobs', 'Central (COBS)'),
        ('crawfordsville', 'Southeast (Crawfordsville)'),
        ('lewis', 'Southwest (Lewis)'),
        ('nashua', 'Northeast (Nashua)'),
        ('sutherland', 'Northwest (Sutherland)')])

SDATES = OrderedDict([
        ('nov1', 'November 1'),
        ('mar15', 'March 15'),
                     ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """ """
    d['arguments'] = [
        dict(type='select', name='location', default='ames',
             label='Select Location:', options=STATIONS),
        dict(type='select', name='s', default='nov1',
             label='Select Plot Start Date:', options=SDATES),
    ]
    return d


def load(dirname, location, sdate):
    """ Read a file please """
    data = []
    idx = []
    for line in open("%s/%s.met" % (dirname, location)):
        line = line.strip()
        if not line.startswith('19') and not line.startswith('20'):
            continue
        tokens = line.split()
        data.append(tokens)
        ts = (datetime.date(int(tokens[0]), 1, 1) +
              datetime.timedelta(days=int(tokens[1])-1))
        idx.append(ts)
    if len(data[0]) < 10:
        cols = ['year', 'doy', 'radn', 'maxt', 'mint', 'rain']
    else:
        cols = ['year', 'doy', 'radn', 'maxt', 'mint',
                'rain', 'gdd', 'st4', 'st12', 'st24',
                'st50', 'sm12', 'sm24', 'sm50']
    df = pd.DataFrame(data, index=idx,
                      columns=cols)
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if len(data[0]) < 10:
        df['gdd'] = gdd(temperature(df['maxt'].values, 'C'),
                        temperature(df['mint'].values, 'C'))
    bins = []
    today = datetime.date.today()
    for valid, _ in df.iterrows():
        if valid >= today:
            bins.append(0)
            continue
        if sdate == 'nov1' and valid.month >= 11:
            bins.append(valid.year+1)
            continue
        if valid.month < today.month:
            bins.append(valid.year)
            continue
        if valid.month == today.month and valid.day < today.day:
            bins.append(valid.year)
            continue
        bins.append(0)
    df['bin'] = bins
    df['rain'] = distance(df['rain'].values, 'MM').value('IN')
    df['avgt'] = temperature(
                    (df['maxt'] + df['mint']) / 2.0, 'C').value('F')
    return df


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt

    location = fdict.get('location', 'ames')
    sdate = fdict.get('s', 'nov1')
    _, _ = STATIONS[location], SDATES[sdate]
    # we need to compute totals using two datasources
    df = load("/mesonet/share/pickup/yieldfx", location, sdate)
    cdf = load("/opt/iem/scripts/yieldfx/baseline",
               location, sdate)

    today = datetime.date.today()

    gdf = df.groupby('bin')['avgt'].mean()
    gdf2 = df.groupby('bin')['rain'].sum()
    gcdf = cdf.groupby('bin')['avgt'].mean()
    gcdf2 = cdf.groupby('bin')['rain'].sum()

    rows = []
    for year in range(1980, today.year + 1):
        if year == 1980 and sdate == 'nov1':
            continue
        if year == today.year:
            avgt = gdf[year]
            rain = gdf2[year]
        else:
            avgt = gcdf[year]
            rain = gcdf2[year]
        rows.append(dict(avgt=avgt, rain=rain, year=year))
    resdf = pd.DataFrame(rows)
    resdf.set_index('year', inplace=True)

    (fig, ax) = plt.subplots(1, 1)
    for year, row in resdf.iterrows():
        color = 'r' if year == today.year else 'k'
        ax.text(row['avgt'], row['rain'], "%s" % (str(year)[-2:],),
                color=color, ha='center', va='center', zorder=4)

    xavg = resdf['avgt'].mean()
    ax.axvline(xavg)
    dx = (resdf['avgt'] - xavg).abs().max()
    ax.set_xlim(xavg - (dx * 1.1), xavg + (dx * 1.1))

    yavg = resdf['rain'].mean()
    ax.axhline(yavg)
    dy = (resdf['rain'] - yavg).abs().max()
    ax.set_ylim(max([0, yavg - (dy * 1.1)]), yavg + (dy * 1.1))

    ax.set_title(("%s %s to %s [%s-%s]"
                  ) % (STATIONS[location],
                       '1 November' if sdate == 'nov1' else '15 March',
                       today.strftime("%-d %B"), 1980,
                       today.year))
    ax.set_xlabel("Average Temperature [$^\circ$F]")
    ax.set_ylabel("Accumulated Precipitation [inch]")
    ax.text(0.15, 0.95, "Cold & Wet", transform=ax.transAxes,
            fontsize=14, color='b', zorder=3, ha='center', va='center')
    ax.text(0.15, 0.05, "Cold & Dry", transform=ax.transAxes,
            fontsize=14, color='b', zorder=3, ha='center', va='center')
    ax.text(0.85, 0.95, "Hot & Wet", transform=ax.transAxes,
            fontsize=14, color='b', zorder=3, ha='center', va='center')
    ax.text(0.85, 0.05, "Hot & Dry", transform=ax.transAxes,
            fontsize=14, color='b', zorder=3, ha='center', va='center')
    ax.grid(True)

    return fig, resdf

if __name__ == '__main__':
    plotter(dict())
