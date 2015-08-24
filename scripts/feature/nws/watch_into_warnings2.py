"""
with watches as (
  SELECT ugc, eventid, issue, expire from warnings WHERE
  phenomena = 'TO' and significance = 'A' and issue > '2005-10-01'),

warnings as (
  SELECT ugc, eventid, issue, expire from warnings where
  phenomena = 'TO' and significance = 'W' and issue > '2005-10-01'),

combo as (
  SELECT a.ugc, a.issue, a.eventid as ae, w.eventid as we
  from watches a LEFT JOIN warnings w on
  (a.ugc = w.ugc and a.issue <= w.issue and a.expire > w.issue)),

combo2 as (
  SELECT ae, extract(year from issue) as yr, min(issue) as minissue,
  sum(case when we is not null then 1 else 0 end) as cnt from combo
  GROUP by ae, yr)

  SELECT extract(month from minissue) as mo,
  sum(case when cnt = 0 then 1 else 0 end),
  count(*) from combo2 GROUP by mo ORDER by mo ASC;

"""

data = """  1 |  6622 |   7453
  2 |  9850 |  12204
  3 | 17635 |  24297
  4 | 43851 |  59998
  5 | 54773 |  81612
  6 | 69593 | 120149
  7 | 51334 |  84414
  8 | 36807 |  55814
  9 | 13021 |  20040
 10 | 10953 |  13955
 11 |  5205 |   6348
 12 |  5462 |   6468"""

ratio = []
h, a = 0, 0
for line in data.split("\n"):
  tokens = line.split("|")
  h += float(tokens[1])
  a += float(tokens[2])
  if float(tokens[2]) == 0:
    ratio.append(0)
  else:
    ratio.append( float(tokens[1]) / float(tokens[2]) * 100.)

import matplotlib.pyplot as plt
import calendar
import numpy as np

(fig, ax) = plt.subplots(1, 1)
ax.bar(np.arange(1, 13)-0.4, ratio)
ax.set_xlim(0.5, 12.5)
for i, r in enumerate(ratio):
  if r > 0:
    ax.text(i+1, r+1, "%.1f%%" % (r, ), ha='center')
ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 25))
ax.grid(True)
ax.set_title(("1 Oct 2005 - 22 Aug 2015 Percent of NWS County Svr Tstorm Warnings"
              "\nthat no SPC Svr Tstorm Watch Active, Overall (%.0f/%.0f %.1f%%)"
              ) % (h, a, h / a * 100.))
ax.set_xticks(range(1, 13))
ax.set_xticklabels(calendar.month_abbr[1:])
ax.set_ylabel("Percentage [%]")
ax.set_xlabel("*based on unofficial IEM archives of NWS WWA")
fig.savefig('test.png')

