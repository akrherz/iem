#!/usr/bin/env python

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
import cStringIO
import psycopg2
import datetime
import numpy as np
import cgi


def make_plot(form):
    """ Make the make_plot """
    year = int(form.getfirst('year', 2013))
    varname = form.getfirst('varname', 'AGR1')[:10]

    pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb',
                              user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""
    SELECT date(updated) as d,
    sum(case when value not in ('.') then 1 else 0 end),
    count(*) from agronomic_data WHERE year = %s
    and varname = %s GROUP by d ORDER by d ASC
    """, (year, varname))
    x = []
    y = []
    total = 0
    for i, row in enumerate(cursor):
        if i == 0:
            x.append(row[0] - datetime.timedelta(days=1))
            y.append(0)
        x.append(row[0])
        y.append(y[-1] + row[1])
        total += row[2]

    xticks = []
    xticklabels = []
    now = x[0]
    while now < x[-1]:
        if now.day == 1:
            fmt = "%b\n%Y" if (len(xticks) == 0 or now.month == 1) else "%b"
            xticks.append(now)
            xticklabels.append(now.strftime(fmt))
        now += datetime.timedelta(days=1)

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(x, np.array(y) / float(total) * 100.)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Percentage [%]")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_title("CSCAP %s Upload Progress for %s" % (varname, year))
    ax.grid(True)


def main():
    """ Make a plot please """
    form = cgi.FieldStorage()
    make_plot(form)

    sys.stdout.write("Content-type: image/png\n\n")

    ram = cStringIO.StringIO()
    plt.savefig(ram, format='png', dpi=100)
    ram.seek(0)
    res = ram.read()
    sys.stdout.write(res)

if __name__ == '__main__':
    # Go Main
    main()
