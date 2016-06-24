"""Edit iowa.txt by hand for now
http://droughtmonitor.unl.edu/MapsAndData/DataTables.aspx
"""
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

df = pd.read_table('iowa.txt')
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values(by='Date', ascending=True, inplace=True)
df.set_index('Date', inplace=True)

(fig, ax) = plt.subplots(1, 1)

# ax.fill_between(valid, d0, 0, facecolor='#f6eb13', label='D0 Abnormal')
ax.bar(df.index.values, df['D0D4'], width=7, fc='#f6eb13', ec='#f6eb13',
       label='D0 Abnormal')
ax.bar(df.index.values, df['D1D4'], width=7, fc='#ffcc66', ec='#ffcc66',
       label='D1 Moderate')
ax.bar(df.index.values, df['D2D4'], width=7, fc='#ff9900', ec='#ff9900',
       label='D2 Severe')
ax.bar(df.index.values, df['D3D4'], width=7, fc='#ff3333', ec='#ff3333',
       label='D3 Extreme')
ax.bar(df.index.values, df['D4'], width=7, fc='#FF00FF', ec='#FF00FF',
       label='D4 Exceptional')
# Duplicate last row
new_index = df.index[-1] + datetime.timedelta(days=7)
df = df.append(pd.DataFrame(index=[new_index],
                            data=df.tail(1).values,
                            columns=df.columns))
for col in ['D0D4', 'D1D4', 'D2D4', 'D3D4', 'D4']:
    ax.step(df.index.values, df[col].values, color='k', where='post')

ax.set_ylim(0, 100)
ax.set_yticks([0, 10, 30, 50, 70, 90, 100])
ax.set_ylabel("Percentage of Iowa Area [%]")
ax.set_title(("2015-2016 Areal coverage of Drought in Iowa\n"
              "from US Drought Monitor thru 23 June 2016"))
ax.grid(True)
ax.set_xlim(datetime.date(2015, 1, 1), datetime.date(2016, 6, 28))
ax.legend(loc=(-0.1, -0.15), ncol=5, prop=prop)
ax.set_position([0.1, 0.15, 0.8, 0.75])
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
fig.savefig('test.png')
