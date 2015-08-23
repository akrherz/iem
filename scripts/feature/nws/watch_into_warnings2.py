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

data = """  1 |  32 |   123
  2 |  33 |   153
  3 |  51 |   256
  4 | 119 |   541
  5 |  86 |   466
  6 |  59 |   361
  7 |  32 |   121
  8 |  24 |   110
  9 |  23 |   116
 10 |  27 |   144
 11 |  38 |   129
 12 |  26 |   118"""

ratio = []
h, a = 0, 0
for line in data.split("\n"):
  tokens = line.split("|")
  h += float(tokens[1])
  a += float(tokens[2])
  ratio.append( float(tokens[1]) / float(tokens[2]) * 100.)

import matplotlib.pyplot as plt
import calendar
import numpy as np

(fig, ax) = plt.subplots(1, 1)
ax.bar(np.arange(1, 13)-0.4, ratio)
ax.set_xlim(0.5, 12.5)
for i, r in enumerate(ratio):
  ax.text(i+1, r+1, "%.1f%%" % (r, ), ha='center')
ax.set_ylim(0, 33)
ax.set_yticks(np.arange(0, 31, 5))
ax.grid(True)
ax.set_title(("1 Oct 2005 - 22 Aug 2015 Percentage of SPC Tornado Watches"
              "\nthat receive no Tornado Warnings, Overall (%.0f/%.0f %.1f%%)"
              ) % (h, a, h / a * 100.))
ax.set_xticks(range(1, 13))
ax.set_xticklabels(calendar.month_abbr[1:])
ax.set_ylabel("Percentage [%]")
ax.set_xlabel("*based on unofficial IEM archives of NWS WWA")
fig.savefig('test.png')

