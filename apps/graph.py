#import matplotlib
#matplotlib.use('Agg')
import datetime
import numpy as np
import matplotlib.colors as colors
import matplotlib.finance as finance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.ticker as t
import MySQLdb
from matplotlib.lines import Line2D

db = MySQLdb.connect(host='166.70.159.134', user='nick', passwd='mohair94', db='market')
curs = db.cursor()

startdate = datetime.date(2009,4,1)
today = enddate = datetime.date.today()
ticker = 'GOOG'

#query="""SELECT date,open,close,high,low,volume from %s where date > 733464 order by date"""%ticker
query="""SELECT date,open,close,high,low,volume from %s where date > 733475 AND date < 733575 order by date"""%ticker
#query="""SELECT date,open,close,high,low,volume from %s order by date"""%ticker
curs.execute(query)

fh = curs.fetchall()
#fh = finance.quotes_historical_yahoo(ticker, startdate, enddate)

plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

textsize = 9
left, width = 0.1, 0.8
rect = [left, 0.1, width, 0.8]

fig = plt.figure(facecolor='white')
axescolor  = '#f6f6f6'  # the axies background color

ax = fig.add_axes(rect, axisbg=axescolor)

last = fh[-1]
s = '%s O:%1.2f H:%1.2f L:%1.2f C:%1.2f' % (
    today.strftime('%d-%b-%Y'),
    last[1], last[3],
    last[4], last[2])
t4 = ax.text(0.3, 0.9, s, transform=ax.transAxes, fontsize=textsize)

finance.candlestick(ax, quotes=fh, width=0.4, colorup='green', colordown='red')
#finance.plot_day_summary(ax, quotes=fh)

ax.set_title('%s Daily'%ticker)


#ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
#ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))

#ax.xaxis.set_major_formatter(t.NullFormatter())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y')) 

for label in ax.get_xticklabels():
    label.set_rotation(30)
    label.set_horizontalalignment('right')

vline1 = Line2D(xdata=[fh[0][0],fh[10][0]], ydata=[fh[0][3],fh[10][3]],color='b',linewidth=1.0,antialiased=True,)
ax.add_line(vline1)

plt.show()
#plt.savefig('/var/www/test2.png')
