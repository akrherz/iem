import matplotlib.pyplot as plt
import iemdb
import datetime

ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

def make_calendar(dates, values):

    (fig, ax) = plt.subplots(1,1, figsize=(5,7))
    plt.setp(ax.get_yticklines(), visible=False)
    plt.setp(ax.get_xticklines(), visible=False)
    ax.xaxis.tick_top()
    ax.set_frame_on(False)

    mindate = min(dates)
    mindate = mindate.replace(day=1)
    #figure out first sunday
    firstsunday = mindate - datetime.timedelta(days=int(mindate.strftime("%w")))

    # Figure out the last date, last sunday
    maxdate = max(dates)
    lastsunday = maxdate + datetime.timedelta(days=7 - int(maxdate.strftime("%w")))
    print firstsunday, lastsunday
    weeks = (lastsunday - firstsunday).days / 7

    for d,v in zip(dates, values):
        weekday = int(d.strftime("%w"))
        week = (d - firstsunday).days / 7
        ax.text(weekday, 0 - week, "%s" % (v,), va='center', ha='center',
                zorder=2, fontsize=20)

    # Labels
    now = datetime.datetime(2013,1,1)
    while now <= datetime.datetime(2013,3,25):
        weekday = int(now.strftime("%w"))
        week = (now - firstsunday).days / 7
        if now.day != 1:
            ax.text(weekday -0.45, 0 - week +0.45, "%s" % (now.day,), fontsize=13, 
                va='top', ha='left', zorder=1, color='tan')
        else:
            ax.text(weekday -0.45, 0 - week +0.45, "1 %s" % (now.strftime("%b"),), fontsize=13, 
                va='top', ha='left', zorder=1, color='lightblue')
        now += datetime.timedelta(days=1)

    # Draw lines
    for week in range(0,-1-weeks,-1):
        ax.plot([-0.5,6.5], [week+0.5, week+0.5], color='k')
    for dow in range(0,7):
        ax.plot([dow-0.5,dow-0.5], [0.5, 0.5 - weeks], color='k')

    ax.set_xlabel("(2013 1 Jan - 25 Mar) Des Moines Hours\nwith Falling Snow Reported" )
    ax.set_xlim(-0.5,6.5)

    ax.set_xticks(range(0,7))
    ax.set_yticklabels([])
    ax.set_xticklabels(["SUN", "MON", "TUE", "WED", "THR", "FRI", "SAT"])
    ax.set_ylim(0.5 - weeks, 0.5)
    plt.tight_layout()

    return fig, ax

acursor.execute("""
 select substr(d,1,8) as day, count(*) from 
  (select distinct to_char(valid, 'YYYYMMDDHH24') as d from t2013 
   where station = 'DBQ' and presentwx ~* 'SN') as foo 
 GROUP by day ORDER by day
""")
dates= []
values = []
for row in acursor:
    d = datetime.datetime.strptime(row[0], '%Y%m%d')
    dates.append( d )
    values.append( row[1] )



(fig, ax) = make_calendar(dates, values)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')