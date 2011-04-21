import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.finance as finance
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.dates import DateFormatter, DayLocator, MONDAY, WeekdayLocator
from matplotlib.dates import *
import numpy

import MySQLdb

import datetime

TRENDRATE = 55
DAYS = 30

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.version = "1.10"
        self.setWindowTitle('Daily Chart')

        self.setup_dbase()
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        # Set variable we can check against later
        self.whole = 0

        self.textbox.setText('Press Next to Start Looking for Trend')

    def setup_dbase(self):
        self.ticker = 'MSFT'
        self.db = MySQLdb.connect(host='ec2-184-73-152-25.compute-1.amazonaws.com', user='nick', passwd='mohair94', db='market')
        self.curs = self.db.cursor()

    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 7x6 inches, 100 dots-per-inch
        #
        self.dpi = 200
        self.fig = Figure((7.0, 7.0), dpi=self.dpi, linewidth=1.0, frameon=True)
        self.canvas = FigureCanvas(self.fig)
#        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(1,1,1)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Other GUI controls
        # 
        self.stockbox = QLineEdit()
        self.stockbox.setMinimumWidth(100)
        self.stockbox.setMaximumWidth(100)

        self.trendlengthbox = QLineEdit()
        self.trendlengthbox.setMinimumWidth(35)
        self.trendlengthbox.setMaximumWidth(35)
        self.trendlengthbox.setText(QString(str(DAYS)))

        self.percentbox = QLineEdit()
        self.percentbox.setMinimumWidth(35)
        self.percentbox.setMaximumWidth(35)
        self.percentbox.setText(QString(str(TRENDRATE)))

        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        
        self.draw_button = QPushButton("&Next")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.trend)
        
        self.stockbutton = QPushButton("&Get Stock")
        self.connect(self.stockbutton, SIGNAL('clicked()'), self.get_stock)
        self.connect(self.stockbox, SIGNAL('returnPressed()'), self.get_stock)

        self.triangle = QCheckBox("Triangle")
        self.triangle.setChecked(True)
        #self.connect(self.triangle_up, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.headandshoulders = QCheckBox("Head and Shoulders")
        self.headandshoulders.setChecked(False)
        #self.connect(self.headandshoulders, SIGNAL('stateChanged(int)'), self.on_draw)

        self.firstdatebox = QDateEdit()

        self.firstdatebox.setDisplayFormat('MM/yyyy')
        self.firstdatebox.setDate(QDate.fromString('012006', 'MMyyyy'))

        self.datebutton = QPushButton("&Change Date")
        self.connect(self.datebutton, SIGNAL('clicked()'), self.change_dates)
                                  
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        hbox12 = QHBoxLayout()
        hbox13 = QHBoxLayout()
        hbox15 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        spacerItem1 = QSpacerItem(0, 50, QSizePolicy.Expanding, QSizePolicy.Minimum)
       
        label = QLabel()
        label.setText("Step 1: Enter Ticker Symbol from Yahoo       ")
        hbox.addWidget(label)
        for w in [  self.stockbox, self.stockbutton ]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        hbox.addItem(spacerItem1)

        label = QLabel()
        label.setText("Step 2: Choose Which Trend to Watch For      ")
        hbox15.addWidget(label)
        for y in [ self.triangle, self.headandshoulders ]:
            hbox15.addWidget(y)
            hbox15.setAlignment(y, Qt.AlignVCenter)
        hbox15.addItem(spacerItem1)

        label = QLabel()
        label.setText("Step 3 (optional): Set Number of Ticks to Watch for Trend  ")
        hbox13.addWidget(label)
        hbox13.addWidget(self.trendlengthbox)
        label = QLabel()
        label.setText("             Set Percent of Change in Ticks to Start Looking for Trend  ")
        hbox13.addWidget(label)
        hbox13.addWidget(self.percentbox)
        hbox13.addItem(spacerItem1)

        label = QLabel()
        label.setText("Step 4: Enter Date to Focus On           ")
        hbox12.addWidget(label)
        for w in [self.firstdatebox, self.datebutton]:
            hbox12.addWidget(w)
            hbox12.setAlignment(w, Qt.AlignVCenter)
        hbox12.addItem(spacerItem1)

        
        for x in [ self.textbox, self.draw_button ]:
            hbox2.addWidget(x)
            hbox2.setAlignment(x, Qt.AlignVCenter)
        
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox15)
        vbox.addLayout(hbox13)
        vbox.addLayout(hbox12)
        vbox.addLayout(hbox2)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("version %s"%self.version)
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def get_stock(self):
        self.ticker = str(self.stockbox.text()).upper()
        startdate = datetime.date(2006,1,1)
        today = datetime.date.today()

        tableexists = True
        stockexists = True

        query="""SHOW TABLES FROM market LIKE '%s'"""%self.ticker
        self.curs.execute(query)
        exists = self.curs.fetchall()
        if exists == ():
            tableexists = False
        if tableexists:
            query="""SELECT date,open,close,high,low,id from %s order by date"""%self.ticker
            self.curs.execute(query)
            self.whole = self.curs.fetchall()
            self.fh = self.whole
        else:
            QMessageBox.information(self, "Hold On", "Stock data is not in database. Fetching data from Yahoo.\n This might take a minute")                        
            insert = finance.quotes_historical_yahoo(self.ticker, startdate, today, adjusted=True)
            if insert == []:
                stockexists = False

        if stockexists and not tableexists:
            self.curs.execute("CREATE TABLE %s(id int AUTO_INCREMENT,date int,open float,close float,high float, low float, volume float, PRIMARY KEY(id))ENGINE=MYISAM;"%self.ticker)
            query="""INSERT INTO %s(date,open,close,high,low,volume) values(%%s,%%s,%%s,%%s,%%s,%%s)"""%self.ticker
            for row in insert:
                self.curs.execute(query,(row[0],row[1],row[2],row[3],row[4],row[5]))
            query="""SELECT date,open,close,high,low,id from %s order by date"""%self.ticker
            self.curs.execute(query)
            self.whole = self.curs.fetchall()
            self.fh = self.whole
            tableexists = True
        elif not stockexists:
            QMessageBox.information(self, "Error", "Could not find a stock with that name on Yahoo")            

        if stockexists and tableexists:
            self.setup_trend()
            self.on_draw()       

    def setup_trend(self):
        DAYS = int(self.trendlengthbox.text())
        TRENDRATE = int(self.percentbox.text())
        try:
            temp = self.fh[0]
        except:
            QMessageBox.information(self, "Error", "Those dates are out of range.")
            return
        self.trianglefound = False
        self.headfound = False
        self.counter = DAYS
        self.pot = 30.0
        self.lastDay = self.fh[0]
        self.boolUP = False
        self.boolDOWN = False
        self.p1date = 0
        self.p1high = 0
        self.p1low = 0
        self.p2date = 0
        self.p2high = 0
        self.p2low = 0
        self.p3date = 0
        self.p3high = 0
        self.p3low = 0
        self.p4date = 0
        self.p4high = 0
        self.p4low = 0
        self.p5date = 0
        self.p5high = 0
        self.p5low = 0
        self.p1set = False
        self.p2set = False
        self.p3set = False
        self.p4set = False
        self.p5set = False
        self.diff = 0
        self.incriment = False
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.p5arrow = False
        self.trendline = False
        self.p13line = False
        self.p24line = False
        self.nodata = False
        self.daysoftrend = 0
        self.maxdays = 10

    def reset_trend(self):
        DAYS = int(self.trendlengthbox.text())
        TRENDRATE = int(self.percentbox.text())
        self.trianglefound = False
        self.headfound = False
        self.boolUP = False
        self.boolDOWN = False
        self.p1date = 0
        self.p1high = 0
        self.p1low = 0
        self.p2date = 0
        self.p2high = 0
        self.p2low = 0
        self.p3date = 0
        self.p3high = 0
        self.p3low = 0
        self.p4date = 0
        self.p4high = 0
        self.p4low = 0
        self.p5date = 0
        self.p5high = 0
        self.p5low = 0
        self.p1set = False
        self.p2set = False
        self.p3set = False
        self.p4set = False
        self.p5set = False
        self.diff = 0
        self.incriment = False
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.p5arrow = False
        self.trendline = True
        self.p13line = False
        self.p24line = False
        self.nodata = False
        self.daysoftrend = 0

    def change_dates(self):
        # Throw error if stock is not loaded
        if self.whole == 0:
            QMessageBox.information(self, "Error", "You must load a stock in before changing dates")
            return                        
        temp =  self.firstdatebox.date()

        t1 = datetime.datetime(temp.year(), temp.month(), temp.day())
        t2 = int(date2num(t1))
        for row in self.whole:
            if t2 <= row[0]:
                firstvalue = row[5]
                break
            
        t1 = datetime.datetime(temp.year(), temp.month(), temp.day())
        t1 += datetime.timedelta(days=150)
        t2 = int(date2num(t1))
        for row in self.whole:
            if t2 <= row[0]:
                lastvalue = row[5]
                break
        try:
            self.fh = self.whole[firstvalue:lastvalue]
        except:
            QMessageBox.information(self, "Error", "The dates are out of range")
            return
        
        self.setup_trend()
        self.trendline = True
        self.textbox.setText('Press Next to Start Looking for Trend')
        self.on_draw()

    def identify_trend(self):
        DAYS = int(self.trendlengthbox.text())
        TRENDRATE = int(self.percentbox.text())
        self.pot = float(DAYS)
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.trendline = True
        self.p13line = False
        self.p24line = False
        up = 0 
        down = 0
        for row in range(self.counter-(DAYS-1),self.counter+1):
            if self.fh[row][2] > self.lastDay[2]:
                up += 1
            else:
                down += 1
            self.lastDay = self.fh[row]

        changeUP = up/self.pot
        changeUP = changeUP * 100
        changeDOWN = down/self.pot
        changeDOWN = changeDOWN * 100
        
        self.p1date = self.lastDay[0]
        self.p1high = self.lastDay[3]
        self.p1low = self.lastDay[4]
        self.p2low = self.p1low
        self.p2high = self.p1high
        self.diff = 0
            
        if changeUP > TRENDRATE and not self.boolUP:
            self.textbox.setText('Upward trend identified. Point 1 set at %.2f'%self.fh[self.counter][3])
            self.boolUP = True
            self.incriment = True
            self.trendline = False
            self.p1arrow = True
            self.p1set = True
        elif changeDOWN > TRENDRATE and not self.boolDOWN:
            self.textbox.setText('Downward trend identified. Point 1 set at %.2f'%self.fh[self.counter][4])
            self.trendline = False
            self.p1arrow = True
            self.boolDOWN = True
            self.incriment = True
            self.p1set = True
        else:
            self.textbox.setText('No trend identified')
            self.incriment = True

    def trend(self):
        try:
            currentDate = self.fh[self.counter][0]
        except:
            # end of graph. Redraw 150 days later
            temp = self.firstdatebox.date()
            t1 = datetime.datetime(temp.year(), temp.month(), temp.day())
            t1 += datetime.timedelta(days=150)
            self.firstdatebox.setDate(QDate.fromString(t1.strftime("%m%Y"), "MMyyyy"))            
            self.change_dates()
            
        currentDate = self.fh[self.counter][0]
        currentClose = self.fh[self.counter][2]
        currentHigh = self.fh[self.counter][3]
        currentLow = self.fh[self.counter][4]

        # No trend identified
        if not self.boolUP and not self.boolDOWN:
            self.daysoftrend = 0
            self.identify_trend()

        # Triangle with a upward trend
        elif self.boolUP and self.triangle.isChecked():
            # Add check into break out of loop if excede max number of days
            self.daysoftrend += 1
            if self.daysoftrend >= self.maxdays:
                QMessageBox.information(self, "Error", "Trend exceded maximum number of days")
                self.reset_trend()
            elif currentHigh > self.p1high:
                self.p2low = self.p1low
                self.boolDOWN = False
                self.boolUP = False
                self.incriment = False
                self.trendline = True
                self.p1arrow = False
                self.p2arrow = False
                self.p3arrow = False
                self.p4arrow = False
                self.p13line = False
                self.p24line = False
                self.p1set = False
                self.p2set = False
                self.p3set = False
                self.p4set = False
                self.p3high = 0
                self.p4low = 0
                self.textbox.setText('New data is higher than Point 1. Starting to look for new trend.')
            elif currentLow < self.p1low and currentLow < self.p2low:
                self.p2date = currentDate
                self.p2low = currentLow
                self.diff = self.p1high - self.p2low
                self.diff = self.diff / 3
                self.diffhigh = self.p1high - self.diff
                self.difflow = self.p2low + self.diff
                self.incriment = True
                self.p2arrow = True
                self.p3arrow = False
                self.p13line = False
                self.p2set = True
                self.p3set = False
                self.p4set = False
                self.daysoftrend = 0
                self.textbox.setText('Point 2 set at %.2f'%self.p2low)
            elif self.p2low < self.p1low and currentHigh > self.diffhigh and currentHigh > self.p3high:
                self.p3date = currentDate
                self.incriment = True
                self.p3high = currentHigh
                self.p4low = currentLow
                self.p3arrow = True
                self.p13line = True
                self.p3set = True
                self.p4set = False
                self.daysoftrend = 0
                self.textbox.setText('Point 3 set at %.2f'%self.p3high)
            elif self.p2set and self.p3set and currentLow < self.difflow and currentLow < self.p4low:
                self.p4date = currentDate
                self.p4low = currentLow
                self.p4arrow = True
                self.p24line = True
                self.incriment = False
                self.daysoftrend = 0
                self.textbox.setText('Point 4 set at %.2f'%self.p4low)
                self.trianglefound = True
                   
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True

        # Triangle with a downward trend
        elif self.boolDOWN and self.triangle.isChecked():
            # Add check into break out of loop if excede max number of days
            self.daysoftrend += 1
            if self.daysoftrend >= self.maxdays:
                QMessageBox.information(self, "Error", "Trend exceded maximum number of days")
                self.reset_trend()
            elif currentLow < self.p1low:
                self.p2high = self.p1high
                self.boolDOWN = False
                self.boolUP = False
                self.incriment = False
                self.trendline = True
                self.p1arrow = False
                self.p2arrow = False
                self.p3arrow = False
                self.p4arrow = False
                self.p13line = False
                self.p24line = False
                self.p1set = False
                self.p2set = False
                self.p3set = False
                self.p4set = False
                self.p3low = 0
                self.p4high = 0
                self.textbox.setText('New data is lower than Point 1. Start looking for new trend.')
            elif currentHigh > self.p1high and currentHigh > self.p2high:
                self.p2date = currentDate
                self.p2high = currentHigh
                self.diff = self.p2high - self.p1low
                self.diff = self.diff / 3
                self.diffhigh = self.p2high - self.diff
                self.difflow = self.p1low + self.diff
                self.incriment = True
                self.p3low = self.difflow
                self.p4high = 0
                self.p2arrow = True
                self.p3arrow = False
                self.p13line = False
                self.p2set = True
                self.p3set = False
                self.p4set = False
                self.daysoftrend = 0
                self.textbox.setText('Point 2 set at %.2f'%self.p2high)
            elif self.p2high > self.p1high and currentLow < self.difflow and currentLow < self.p3low:
                self.p3date = currentDate
                self.incriment = True
                self.p3low = currentLow
                self.p4high = currentHigh
                self.p3arrow = True
                self.p13line = True
                self.p2set = True
                self.p3set = True
                self.p4set = False
                self.daysoftrend = 0
                self.textbox.setText('Point 3 set at %.2f'%self.p3low)
            elif self.p2set and self.p3set and currentHigh > self.diffhigh and currentHigh > self.p4high:
                self.p4date = currentDate
                self.p4high = currentHigh
                self.p4arrow = True
                self.p24line = True
                self.incriment = False
                self.daysoftrend = 0
                self.textbox.setText('Point 4 set at %.2f'%self.p4high)
                self.trianglefound = True               
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True
                self.incriment = True

        # Head and Shoulders trend with an upward trend
        elif self.boolUP and self.headandshoulders.isChecked():
            if currentHigh > self.p1high and not self.p2set:
                self.p2low = self.p1low
                self.boolDOWN = False
                self.boolUP = False
                self.incriment = False
                self.trendline = True
                self.p1arrow = False
                self.p2arrow = False
                self.p3arrow = False
                self.p4arrow = False
                self.p5arrow = False
                self.p13line = False
                self.p24line = False
                self.p1set = False
                self.p2set = False
                self.p3set = False
                self.p4set = False
                self.p5set = False
                self.p3high = 0
                self.p4low = 0
                self.textbox.setText('New data is higher than Point 1. Start looking for new trend. HeadandShoulders')
            elif currentLow < self.p1low and currentLow < self.p2low and self.p1set:
                self.p2low = currentLow
                self.p2date = currentDate
                self.diff = self.p1high - self.p2low
                self.diff = self.diff / 3
                self.diffhigh = self.p1high - self.diff
                self.difflow = self.p2low + self.diff
                self.p3high = self.p1high
                self.p2arrow = True
                self.p3arrow = False
                self.p4arrwo = False
                self.p5arrow = False
                self.p2set = True
                self.p3set = False
                self.p4set = False
                self.p5set = False
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 2 set at %.2f'%self.p2low)            
            # Set point 3
            elif currentHigh > self.p3high and self.p1set and self.p2set and not self.p3set:
                self.p3high = currentHigh
                self.p3date = currentDate
                self.p3arrow = True
                self.p3set = True
                self.p4low = self.p1high
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 3 set at %.2f'%self.p3high)

#           Test against point 3 to see if point it higher than the current point 3
            elif currentLow > self.p3high and self.p1set and self.p2set and self.p3set:
                self.p3high = currentHigh
                self.p3date = currentDate
                self.p3arrow = True
                self.p3set = True
                self.p4low = self.p1high
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 3 set at %.2f'%self.p3high)
            # Set point 4
            elif currentLow < self.p4low and self.p1set and self.p2set and self.p3set and not self.p4set:
                self.p4date = currentDate
                self.p4set = True
                self.p4low = currentLow
                self.p24line = True
                self.p4arrow = True
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 4 set at %.2f'%self.p4low)            
            elif currentHigh > self.p1high and currentHigh < self.p3high and self.p1set and self.p2set and self.p3set and self.p4set:
                self.p5high = currentHigh
                self.p5set = True
                self.p5date = currentDate
                self.p5arrow = True
                self.daysoftrend = 0
                self.textbox.setText('Point 5 set at %.2f'%self.p5high)
                self.headfound = True               
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True
                self.incriment = True

        # Head and shoulders with downward trend
        elif self.boolDOWN and self.headandshoulders.isChecked():
#            if currentHigh > self.p1high and not self.p2set:
            if currentLow < self.p1low and not self.p2set:
                self.p2low = self.p1low
                self.boolDOWN = False
                self.boolUP = False
                self.incriment = False
                self.trendline = True
                self.p1arrow = False
                self.p2arrow = False
                self.p3arrow = False
                self.p4arrow = False
                self.p5arrow = False
                self.p13line = False
                self.p24line = False
                self.p1set = False
                self.p2set = False
                self.p3set = False
                self.p4set = False
                self.p5set = False
                self.p3high = 0
                self.p4low = 0
                self.textbox.setText('New data is lower than Point 1. Start looking for new trend.')
#            elif currentLow < self.p1low and currentLow < self.p2low and self.p1set:
            elif currentHigh > self.p1high and currentHigh > self.p2high and self.p1set:
                self.p2high = currentHigh
                self.p2low = currentLow
                self.p2date = currentDate
#                self.diff = self.p1high - self.p2low
                self.diff = self.p1high - self.p2low
                self.diff = self.diff / 3
                self.diffhigh = self.p1high - self.diff
                self.difflow = self.p2low + self.diff
                self.p3low = self.p1low
                self.p4high = self.p4high
                self.p2arrow = True
                self.p3arrow = False
                self.p4arrow = False
                self.p5arrow = False
                self.p2set = True
                self.p3set = False
                self.p4set = False
                self.p5set = False
                self.daysoftrend = 0
                self.textbox.setText('Point 2 set at %.2f'%self.p2high)            
#           Set point 3
            elif currentLow < self.p3low and self.p1set and self.p2set and not self.p3set:
                self.p3high = currentHigh
                self.p3low = currentLow
                self.p3date = currentDate
                self.p3arrow = True
                self.p4arrow = False
                self.p5arrwo = False
                self.p3set = True
                self.p4set = False
                self.p5set = False
                self.p4high = self.p1low
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 3 set at %.2f'%self.p3low)            
#           Test against point 3 to see if point it lower than the current point 3
            elif currentLow < self.p3low and self.p1set and self.p2set and self.p3set:
                self.p3high = currentHigh
                self.p3low = currentLow
                self.p3date = currentDate
                self.p3arrow = True
                self.p4arrow = False
                self.p5arrwo = False
                self.p3set = True
                self.p4set = False
                self.p5set = False
                self.p4high = self.p1low
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 3 set at %.2f'%self.p3low)   
#           Set point 4
            elif currentHigh > self.p4high and self.p1set and self.p2set and self.p3set and not self.p4set:
                self.p4date = currentDate
                self.p4set = True
                self.p5set = False
                self.p4low = currentLow
                self.p4high = currentHigh
                self.p24line = True
                self.p4arrow = True
                self.p5arrow = False
                self.daysoftrend = 0
                self.textbox.setText('HEAD Point 4 set at %.2f'%self.p4high)            
#            elif currentHigh > self.p1high and currentHigh < self.p3high and self.p1set and self.p2set and self.p3set and self.p4set:
            elif currentLow < self.p1low and currentLow > self.p3low and self.p1set and self.p2set and self.p3set and self.p4set and not self.p5set:
                self.p5high = currentHigh
                self.p5low = currentLow
                self.p5set = True
                self.p5date = currentDate
                self.p5arrow = True
                self.daysoftrend = 0
                self.textbox.setText('Point 5 set at %.2f'%self.p5low)
                self.headfound = True
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True
                self.incriment = True
                
        self.on_draw()

    def on_draw(self):
        DAYS = int(self.trendlengthbox.text())
        TRENDRATE = int(self.percentbox.text())
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        try:
            diff = self.fh[-1][0] - self.fh[0][0]
        except:
            return
        
        if diff > 180:
            x = []
            y = []
            for data in self.fh:
                x.append(data[0])
                y.append(data[2])
            self.axes.plot(x,y)
            self.axes.xaxis.set_major_locator(YearLocator())
            self.axes.xaxis.set_major_formatter(DateFormatter('%Y'))
            self.axes.xaxis.set_minor_locator(MonthLocator())
        elif diff <= 180 and diff > 100:
            finance.candlestick(self.axes, quotes=self.fh, width=0.4, colorup='green', colordown='red')
            self.axes.xaxis.set_major_locator(MonthLocator()) # major ticks on the mondays
            self.axes.xaxis.set_minor_locator(WeekdayLocator(MONDAY)) # minor ticks on the days
            self.axes.xaxis.set_major_formatter(DateFormatter('%b')) # Eg, Jan 12
        else:
            finance.candlestick(self.axes, quotes=self.fh, width=0.4, colorup='green', colordown='red')
            self.axes.xaxis.set_major_locator(WeekdayLocator(MONDAY)) # major ticks on the mondays
            self.axes.xaxis.set_minor_locator(DayLocator()) # minor ticks on the days
            self.axes.xaxis.set_major_formatter(DateFormatter('%b %d')) # Eg, Jan 12

        if self.trendline:
            self.axes.annotate('Start', xy=(self.fh[self.counter-DAYS][0],self.fh[self.counter-DAYS][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->")) 
            self.axes.annotate('End', xy=(self.fh[self.counter][0],self.fh[self.counter][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))         

        if self.p1arrow and self.boolUP and self.triangle.isChecked():
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1high), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolUP and self.triangle.isChecked():
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolUP and self.triangle.isChecked():
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3high), xytext=(-10,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolUP and self.triangle.isChecked():
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             

        if self.p1arrow and self.boolDOWN and self.triangle.isChecked():
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1low), xytext=(-10,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolDOWN and self.triangle.isChecked():
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolDOWN and self.triangle.isChecked():
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3low), xytext=(-10,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolDOWN and self.triangle.isChecked():
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             

        if self.p1arrow and self.boolUP and self.headandshoulders.isChecked():
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1high), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolUP and self.headandshoulders.isChecked():
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolUP and self.headandshoulders.isChecked():
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3high), xytext=(-10,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolUP and self.headandshoulders.isChecked():
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p5arrow and self.boolUP and self.headandshoulders.isChecked():
            self.axes.annotate('Point 5', xy=(self.p5date,self.p5high), xytext=(0,30), xycoords='data', textcoords='offset points', arrowprops=dict(arrowstyle="->"))

        if self.p1arrow and self.boolDOWN and self.headandshoulders.isChecked():
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1low), xytext=(-30,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolDOWN and self.headandshoulders.isChecked():
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolDOWN and self.headandshoulders.isChecked():
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3low), xytext=(-30,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolDOWN and self.headandshoulders.isChecked():
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p5arrow and self.boolDOWN and self.headandshoulders.isChecked():
            self.axes.annotate('Point 5', xy=(self.p5date,self.p5low), xytext=(-10,-30), xycoords='data', textcoords='offset points', arrowprops=dict(arrowstyle="->"))

        if self.p13line and self.boolUP and self.triangle.isChecked():
            line1 = Line2D(xdata=[self.p1date,self.p3date], ydata=[self.p1high,self.p3high],color='b',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)
        if self.p24line and self.boolUP:
            line1 = Line2D(xdata=[self.p2date,self.p4date], ydata=[self.p2low,self.p4low],color='r',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)

        if self.p13line and self.boolDOWN and self.triangle.isChecked():
            line1 = Line2D(xdata=[self.p1date,self.p3date], ydata=[self.p1low,self.p3low],color='b',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)
        if self.p24line and self.boolDOWN:
            line1 = Line2D(xdata=[self.p2date,self.p4date], ydata=[self.p2high,self.p4high],color='r',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)

        if self.nodata:
            highlight = Line2D(xdata=(self.fh[self.counter][0],self.fh[self.counter][0]), ydata=(self.fh[self.counter][3],self.fh[self.counter][4]), color='blue')
            if self.fh[self.counter][2] >= self.fh[self.counter][1]:
                lower = self.fh[self.counter][1]
                height = self.fh[self.counter][2] - self.fh[self.counter][1]
            else:
                lower = self.fh[self.counter][2]
                height = self.fh[self.counter][1] - self.fh[self.counter][2]
            rect = Rectangle(xy=(self.fh[self.counter][0]-0.3,lower),width=0.6,height=height,facecolor='blue',edgecolor='blue')
    
            self.axes.add_line(highlight)
            self.axes.add_patch(rect)
            self.nodata = False

        self.axes.set_title('%s Daily'%self.ticker)
        self.axes.xaxis_date()

        for label in self.axes.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')

        self.axes.grid()
        
        self.canvas.draw()

        if self.trianglefound:
            QMessageBox.information(self, "Alert", "Triangle Trend Found.")

        if self.headfound:            
            QMessageBox.information(self, "Alert", "Head and Shoulders Trend Found.")
            
        if self.p24line and self.triangle.isChecked():
            self.reset_trend()

        if self.p5set and self.headandshoulders.isChecked():
            self.reset_trend()
            
        if self.incriment:
            self.counter += 1
    
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = "Version %s"%self.version

        QMessageBox.about(self, "About..", msg.strip())
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)


    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
