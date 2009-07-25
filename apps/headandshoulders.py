import MySQLdb
import time
import sys

ticker="GOOG"

db = MySQLdb.connect(host="166.70.159.134", user="nick", passwd="mohair94", db="market")
curs = db.cursor()

#query="""SELECT id,high,low,close from %s order by date"""%ticker
#query="""SELECT id,high,low,close from %s where date > 733464 order by date"""%ticker
query="""SELECT id,high,low,close from %s where date > 733475 AND date < 733575 order by date"""%ticker
#query="""SELECT id,high,low,close from %s where id > 500 AND id < 600 order by date"""%ticker
curs.execute(query)

mData = curs.fetchall()

counter=21
pot = 20.0
lastDay =  mData[0]
boolUP = False
boolDOWN = False
finish = False

while (not finish):
    raw_input()
    counter += 1
    up = 0
    down = 0
    if not boolUP and not boolDOWN:
        for row in range(counter-20,counter):
            if mData[row][3] > lastDay[3]:
                up += 1
            else:
                down += 1
            lastDay = mData[row]

        changeUP = up/pot
        changeUP = changeUP * 100
        changeDOWN = down/pot
        changeDOWN = changeDOWN * 100

        p1low = lastDay[2]
        p1high = lastDay[1]
        p2low = p1low
        p3high = 0
        p4low = p1high
        p5high = 0
        diff = 0        
        diffhigh = 0
        difflow = 0
        p2blow = False
        p3bhigh = False
        p3blow = False
        p4bhigh = False
        p4blow = False

        print "-------------------------------"
        print "UP = " + str(up)
        print "DOWN = " + str(down)

        if changeUP > 55 and not boolUP:
            print "Value of point1 HIGH=%.2f LOW=%.2f CLOSE=%.2f" % (lastDay[1], lastDay[2], lastDay[3])
            print "Upward trend identified. Percent of change = %.2f" % (changeUP)
            print "--------------------------------"
            boolUP = True

        elif changeDOWN > 55 and not boolDOWN:
            print "Value of point1 HIGH=%.2f LOW=%.2f CLOSE=%.2f" % (lastDay[1], lastDay[2], lastDay[3])
            print "Downward trend identified. Percent of change = %.2f" % (changeDOWN)
            print "--------------------------------"
            boolDOWN = True

        else:
            print "HIGH=%.2f LOW=%.2f CLOSE=%.2f" % (lastDay[1], lastDay[2], lastDay[3])
            print "Not a trend"
            print "Percentage Down = %.2f Percentage UP = %.2f"%(changeDOWN,changeUP)

            raw_input()

    


    if boolUP or boolDOWN:
        print "New Data Recieved - HIGH=%.2f LOW=%.2f CLOSE=%.2f" % (mData[counter][1], mData[counter][2], mData[counter][3])
        print "Values p1high = %.2f p1low = %.2f p2low = %.2f p2blow = %s p3high = %.2f"%(p1high, p1low, p2low,p2blow, p3high)
        # Sets point 1
        if mData[counter][1] > p1high and not p2blow:
            p2low = p1low
            boolDOWN = False
            boolUP = False
            print "New data is higher than Point 1. Starting new trend"
        # Sets point 2 
        elif mData[counter][2] < p1low and mData[counter][2] < p2low:
            p2low = mData[counter][2]
            print "Point 2 Low %.2f" % (p2low)    
            diff = p1high - p2low
            diff = diff / 3
            diffhigh = p1high - diff
            difflow = p2low + diff
            p3high = p1high
            p2blow = True
        # Test point 3
        elif mData[counter][1] > p3high and p2blow and not p3blow:
            p3high = mData[counter][1]
            p3bhigh = True
            print "p3high set"
        elif mData[counter][2] < p1high and p2blow and p3bhigh and not p3blow:
            p3blow = True
            p3bhigh = True
            print "Point 3 is set. High %.2f" % (p3high)
        # Sets point 4
        elif mData[counter][2] < p4low and p2blow and p3blow and p3bhigh and not p4bhigh:            
            p4blow = True
            p4low = mData[counter][2]
            print "p4low is set"
        elif mData[counter][1] > p1high and p2blow and p3blow and p3bhigh and p4blow and not p4bhigh:
            p4bhigh = True
            print "Point 4 is set. Low %.2f" % (p4low)
        elif mData[counter][2] < p4low and p2blow and p3blow and p3bhigh and p4blow and p4bhigh:
            p4low = mData[counter][2]
            print "New Point 4 is set %.2f" % (p4low)
        elif mData[counter][1] > p1high and mData[counter][1] < p3high and p2blow and p3blow and p3bhigh and p4blow and p4bhigh:
            p5high = mData[counter][1]
            print "Point 5 set. ALERT"
            boolUP = False
            boolDOWN = False
#        elif p2low < p1low and mData[counter][1] > diffhigh and mData[counter][1] > p3high:
#            p3high = mData[counter][1]
#            p4low = mData[counter][2]
#            print "Point 3 High %.2f" % (p3high)
        # Sets point 4
#        elif p2low > 0 and p3high > 0 and mData[counter][2] < difflow and mData[counter][2] < p4low:
#            p4low = mData[counter][2]
#            print "Point 4 Low %.2f" % (p4low)
#            boolUP = False
#            boolDOWN = False
    print "--------------------------------"
