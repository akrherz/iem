"""
with data as (
    select
substring(data from '\.\.\.([0-9]{1,3}) (PERCENT|percent)') as d from products
    WHERE pil = 'SWOMCD' and entered > '2012-05-01')
SELECT d, count(*) from data GROUP by d ORDER by d
 20 |  1902
 40 |  1450
 5  |   860
 60 |   717
 80 |   656
 95 |   313
    |  4551
"""

import matplotlib.pyplot as plt
import numpy as np

data = [860, 1902, 1450, 717, 656, 313, 4551]
cats = ['5%', '20%', '40%', '60%', '80%', '95%', 'No\nMention']
total = float(sum(data))
(fig, ax) = plt.subplots(1, 1)

ax.set_ylim(0, max(data) * 1.2)
ax.bar(np.arange(7), data, align='center')
for i in range(7):
    val = "\n%.1f%%" % (data[i] / float(sum(data[:-1])) * 100.,)
    ax.text(i, data[i] + 250, "%s\n%.1f%%%s" % (data[i],
                                                data[i] / total * 100.,
            val if i < 6 else ''),
            va='bottom', ha='center', bbox=dict(color='#EEEEEE'))
ax.set_xticks(range(7))
ax.text(0.05, 0.95, 'Count\n% of Total\n% of non-No Mention Total',
        ha='left', va='top', bbox=dict(color='#EEEEEE'),
        transform=ax.transAxes)
ax.set_xticklabels(cats)
ax.grid(True)
ax.set_title(("Storm Prediction Center :: "
              "Mesoscale Discussion\nWatch Confidence "
              "(%.0f total, 1 May 2012 - 27 Mar 2017)") % (total, ))
ax.set_ylabel("Frequency (Product Count)")
# ax.set_xlabel("Value mentioned in text")

fig.text(0.01, 0.01,
         "@akrherz, based on unofficial IEM archives, generated 27 March 2017")
fig.savefig('test.png')
