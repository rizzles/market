import csv
import MySQLdb

print "test"
db = MySQLdb.connect(host='166.70.159.134', user='nick', passwd='mohair94', db='market')
curs = db.cursor()

file = open("data.csv", "rU")
marketData = csv.reader(file)
for row in marketData:
    curs.execute("INSERT INTO euro(high, low, close) values(%s, %s, %s)", (row[0], row[1], row[2]))
    print row

