import datetime
import numpy as np
import matplotlib.colors as colors
import matplotlib.finance as finance
import MySQLdb

db = MySQLdb.connect(host='166.70.159.134', user='nick', passwd='mohair94', db='market')
curs = db.cursor()

startdate = datetime.date(2007,1,1)
today = enddate = datetime.date.today()
ticker = 'GOOG'


fh = finance.quotes_historical_yahoo(ticker, startdate, enddate, adjusted=True)

curs.execute("DROP TABLE IF EXISTS %s"%ticker)
curs.execute("CREATE TABLE %s(id int AUTO_INCREMENT,date int,open float,close float,high float, low float, volume float, PRIMARY KEY(id))ENGINE=MYISAM;"%ticker)

query="""INSERT INTO %s(date,open,close,high,low,volume) values(%%s,%%s,%%s,%%s,%%s,%%s)"""%ticker

for row in fh:
    curs.execute(query,(row[0],row[1],row[2],row[3],row[4],row[5]))

