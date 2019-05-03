"""USDM Filled Time Series"""
import datetime

import requests
import pandas as pd
import matplotlib.dates as mdates
from pyiem import util
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names, state_fips

SERVICE = (
    "https://droughtmonitor.unl.edu"
    "/Ajax2018.aspx/ReturnTabularDMAreaPercent_"
)
COLORS = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]
PDICT = {
       'state': 'Plot Individual State',
       'national': 'Plot CONUS',
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot presents a time series of areal coverage
    of United States Drought Monitor for a given state of your choice. This
    plot uses a JSON data service provided by the
    <a href="http://droughtmonitor.unl.edu">Drought Monitor</a> website.
    """
    today = datetime.datetime.today()
    sts = today - datetime.timedelta(days=720)
    desc['arguments'] = [
        dict(type='select', default='state', name='s', options=PDICT,
             label='Plot for state or CONUS:'),
        dict(type='state', name='state', default='IA',
             label='Select State:'),
        dict(type='date', name='sdate',
             default=sts.strftime("%Y/%m/%d"),
             label='Start Date:', min="2000/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date:', min="2000/01/01"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = util.get_autoplot_context(fdict, get_description())
    sdate = ctx['sdate']
    edate = ctx['edate']
    state = ctx['state']

    fips = ''
    for key in state_fips:
        if state_fips[key] == state:
            fips = key
    if ctx['s'] == 'state':
        payload = "{'area':'%s', 'type':'state', 'statstype':'2'}" % (fips, )
    else:
        payload = "{'area':'conus', 'statstype':'2'}"
    headers = {}
    headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
    headers['Content-Type'] = "application/json; charset=UTF-8"
    req = requests.post(SERVICE + ctx['s'], payload, headers=headers)
    jdata = req.json()
    df = pd.DataFrame(jdata['d'])
    df['Date'] = pd.to_datetime(df['ReleaseDate'])
    df = df[(df['Date'] >= pd.Timestamp(sdate)) &
            (df['Date'] <= pd.Timestamp(edate))]
    df.sort_values('Date', ascending=True, inplace=True)
    df['x'] = df['Date'] + datetime.timedelta(hours=(3.5*24))
    df.set_index('Date', inplace=True)
    df.index.name = 'Date'

    (fig, ax) = plt.subplots(1, 1)

    xs = df['x'].values
    bottom = (df['D4'] + df['D3'] + df['D2'] + df['D1']).values
    ax.bar(xs, df['D0'], width=7, fc=COLORS[0], ec='None', bottom=bottom,
           label='D0 Abnormal')
    bottom = (df['D4'] + df['D3'] + df['D2']).values
    ax.bar(xs, df['D1'], bottom=bottom, width=7, fc=COLORS[1],
           ec='None',
           label='D1 Moderate')
    bottom = (df['D4'] + df['D3']).values
    ax.bar(xs, df['D2'], width=7,
           fc=COLORS[2], ec='None', bottom=bottom,
           label='D2 Severe')
    bottom = df['D4'].values
    ax.bar(xs, df['D3'],
           width=7, fc=COLORS[3], ec='None', bottom=bottom,
           label='D3 Extreme')
    ax.bar(xs, df['D4'],
           width=7, fc=COLORS[4], ec='None',
           label='D4 Exceptional')

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 30, 50, 70, 90, 100])
    ax.set_ylabel("Percentage of Iowa Area [%]")
    df.reset_index(inplace=True)
    ax.set_title(("Areal coverage of Drought for %s\n"
                  "from US Drought Monitor %s - %s"
                  ) % (state_names[state] if ctx['s'] == 'state' else 'CONUS',
                       df['Date'].min().strftime("%-d %B %Y"),
                       df['Date'].max().strftime("%-d %B %Y")))
    ax.grid(True)
    ax.set_xlim(df['Date'].min(),
                df['Date'].max() + datetime.timedelta(days=7))
    ax.legend(loc=(0.1, -0.3), ncol=3)
    ax.set_position([0.1, 0.25, 0.8, 0.65])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

    return fig, df[['Date', 'NONE', 'D0', 'D1', 'D2', 'D3', 'D4']]


if __name__ == '__main__':
    plotter(dict())
