"""Edit iowa.txt by hand for now
http://droughtmonitor.unl.edu/MapsAndData/DataTables.aspx
"""
from __future__ import print_function

import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

COLORS = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]


def main():
    """Go Main"""

    df = pd.read_table('iowa.txt')
    df['Date'] = pd.to_datetime(df['Date'])
    df['x'] = df['Date'] + datetime.timedelta(hours=(3.5*24))
    df.sort_values(by='Date', ascending=True, inplace=True)
    df.set_index('Date', inplace=True)

    (fig, ax) = plt.subplots(1, 1)

    xs = df['x'].values
    ax.bar(xs, df['D0'], width=7, fc=COLORS[0], ec='None',
           label='D0 Abnormal')
    bottom = df['D0'].values
    ax.bar(xs, df['D1'], bottom=bottom, width=7, fc=COLORS[1],
           ec='None',
           label='D1 Moderate')
    bottom = (df['D1'] + df['D0']).values
    ax.bar(xs, df['D2'], width=7,
           fc=COLORS[2], ec='None', bottom=bottom,
           label='D2 Severe')
    bottom = (df['D2'] + df['D1'] + df['D0']).values
    ax.bar(xs, df['D3'],
           width=7, fc=COLORS[3], ec='None', bottom=bottom,
           label='D3 Extreme')
    bottom = (df['D3'] + df['D2'] + df['D1'] + df['D0']).values
    ax.bar(xs,
           df['D4'],
           width=7, fc=COLORS[4], ec='None', bottom=bottom,
           label='D4 Exceptional')
    # Duplicate last row
    new_index = df.index[-1] + datetime.timedelta(days=7)
    df = df.append(pd.DataFrame(index=[new_index],
                                data=df.tail(1).values,
                                columns=df.columns))

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 30, 50, 70, 90, 100])
    ax.set_ylabel("Percentage of Iowa Area [%]")
    ax.set_title(("Areal coverage of Drought in Iowa\n"
                  "from US Drought Monitor 1 June 2016 - 12 July 2017"))
    ax.grid(True)
    ax.set_xlim(datetime.date(2016, 6, 1), datetime.date(2017, 7, 20))
    ax.legend(loc=(0.1, -0.3), ncol=3)
    ax.set_position([0.1, 0.25, 0.8, 0.65])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
