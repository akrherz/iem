import pandas as pd
from StringIO import StringIO
import matplotlib.pyplot as plt

# select precip, sum(precip), count(*) from alldata_1minute
# where station = 'DSM' and precip > 0 GROUP by precip ORDER by precip ASC;
data = StringIO("""rate | total | count
   0.01 | 342.113 | 34209
   0.02 | 54.7011 |  2735
   0.03 | 34.7702 |  1159
   0.04 | 24.3202 |   608
   0.05 |    18.1 |   362
   0.06 |   11.82 |   197
   0.07 | 8.54001 |   122
   0.08 |    5.84 |    73
   0.09 |    3.87 |    43
    0.1 |     2.4 |    24
   0.11 |    1.54 |    14
   0.12 |    1.32 |    11
   0.13 |    0.78 |     6
   0.14 |    0.14 |     1
   0.15 |    0.15 |     1
   0.16 |    0.48 |     3
   0.17 |    0.34 |     2
   0.18 |    0.18 |     1
    0.2 |     0.4 |     2
   0.21 |    0.63 |     3""")

df = pd.read_csv(data, sep=r"\s+\|\s+", engine='python')
df['total_ratio'] = df['total'] / df['total'].sum() * 100.
df['count_ratio'] = df['count'] / df['count'].sum() * 100.

(fig, ax) = plt.subplots(2, 1)

ax[0].bar(df['rate'].values, df['total_ratio'], align='edge', color='b',
          width=0.0035, label='Total Rain Volume')
ax[0].bar(df['rate'].values, df['count_ratio'], align='edge', color='r',
          width=-0.0035, label='Total Count')
ax[0].set_ylabel("Contribution Percentage [%]")
ax[0].set_title("2000-2016 Des Moines Precipitation Contributions")
ax[0].legend()
ax[0].grid(True)

ax[1].bar(df['rate'].values, df['total_ratio'], align='edge', color='b',
          width=0.0035, label='Total Rain Volume')
ax[1].bar(df['rate'].values, df['count_ratio'], align='edge', color='r',
          width=-0.0035, label='Total Count')
ax[1].set_xlabel("One Minute Accumulation [inch]")
ax[1].set_ylabel("Contribution Percentage [%]")
ax[1].set_yscale("log")
ax[1].grid(True)
ax[1].text(0.7, 0.7, "Same Data As Above\nJust Log Scale",
           transform=ax[1].transAxes)
fig.savefig('test.png')
