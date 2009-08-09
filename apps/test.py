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

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.version = "14"
        self.setWindowTitle('Daily Chart')

        self.setup_dbase()
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.textbox.setText('Press Next to Start Looking for Trend')

    def setup_dbase(self):
        self.ticker = 'MSFT'
        self.db = MySQLdb.connect(host='166.70.159.134', user='nick', passwd='mohair94', db='market')
        self.curs = self.db.cursor()

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
        self.counter = 30
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
        self.p1set = False
        self.p2set = False
        self.p3set = False
        self.p4set = False
        self.diff = 0
        self.incriment = False
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.trendline = False
        self.p13line = False
        self.p24line = False
        self.nodata = False

    def change_dates(self):
        temp =  self.firstdatebox.date()
        t1 = datetime.datetime(temp.year(), temp.month(), temp.day())
        t2 = int(date2num(t1))
        for row in self.whole:
            if t2 <= row[0]:
                firstvalue = row[5]
                break
        temp = self.lastdatebox.date()
        t1 = datetime.datetime(temp.year(), temp.month(), temp.day())
        t2 = int(date2num(t1))
        for row in self.whole:
            if t2 <= row[0]:
                lastvalue = row[5]
                break
        self.fh = self.whole[firstvalue:lastvalue]
        self.setup_trend()
        self.trendline = True
        self.textbox.setText('Press Next to start looking for trend.')
        self.on_draw()

    def identify_trend(self):
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.trendline = True
        self.p13line = False
        self.p24line = False
        up = 0 
        down = 0
        for row in range(self.counter-29,self.counter+1):
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
            
        if changeUP > 55 and not self.boolUP:
            self.textbox.setText('Upward trend identified. Point 1 set at %.2f'%self.fh[self.counter][3])
            self.boolUP = True
            self.incriment = True
            self.trendline = False
            self.p1arrow = True
            self.p1set = True
        elif changeDOWN > 55 and not self.boolDOWN:
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
        if not self.boolUP and not self.boolDOWN:
            self.identify_trend()
#        elif self.boolUP or self.boolDOWN:
        elif self.boolUP:
            if self.fh[self.counter][3] > self.p1high:
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
                self.p3high = 0
                self.p4low = 0
                self.textbox.setText('New data is higher than Point 1. Start looking for new trend.')
            elif self.fh[self.counter][4] < self.p1low and self.fh[self.counter][4] < self.p2low:
                self.p2date = self.fh[self.counter][0]
                self.p2low = self.fh[self.counter][4]
                self.diff = self.p1high - self.p2low
                self.diff = self.diff / 3
                self.diffhigh = self.p1high - self.diff
                self.difflow = self.p2low + self.diff
                self.incriment = True
                self.p2arrow = True
                self.p3arrow = False
                self.p13line = False
                self.textbox.setText('Point 2 set at %.2f'%self.p2low)
            elif self.p2low < self.p1low and self.fh[self.counter][3] > self.diffhigh and self.fh[self.counter][3] > self.p3high:
                self.p3date = self.fh[self.counter][0]
                self.incriment = True
                self.p3high = self.fh[self.counter][3]
                self.p4low = self.fh[self.counter][4]
                self.p3arrow = True
                self.p13line = True
                self.textbox.setText('Point 3 set at %.2f'%self.p3high)
            elif self.p2low > 0 and self.p3high > 0 and self.fh[self.counter][4] < self.difflow and self.fh[self.counter][4] < self.p4low:
                self.p4date = self.fh[self.counter][0]
                self.p4low = self.fh[self.counter][4]
                self.p4arrow = True
                self.p24line = True
                self.incriment = False
                self.textbox.setText('Point 4 set at %.2f'%self.p4low)
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True

        elif self.boolDOWN:
            if self.fh[self.counter][4] < self.p1low:
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
#            elif self.fh[self.counter][4] < self.p1low and self.fh[self.counter][4] < self.p2low:
            elif self.fh[self.counter][3] > self.p1high and self.fh[self.counter][3] > self.p2high:
                self.p2date = self.fh[self.counter][0]
                self.p2high = self.fh[self.counter][3]
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
                self.textbox.setText('Point 2 set at %.2f'%self.p2high)
#            elif self.p2low < self.p1low and self.fh[self.counter][3] > self.diffhigh and self.fh[self.counter][3] > self.p3high:
            elif self.p2high > self.p1high and self.fh[self.counter][4] < self.difflow and self.fh[self.counter][4] < self.p3low:
                self.p3date = self.fh[self.counter][0]
                self.incriment = True
                self.p3low = self.fh[self.counter][4]
                self.p4high = self.fh[self.counter][3]
                self.p3arrow = True
                self.p13line = True
                self.p2set = True
                self.p3set = True
                self.p4set = False
                self.textbox.setText('Point 3 set at %.2f'%self.p3low)
#            elif self.p2low > 0 and self.p3high > 0 and self.fh[self.counter][4] < self.difflow and self.fh[self.counter][4] < self.p4low:
            elif self.p2set and self.p3set and self.fh[self.counter][3] > self.diffhigh and self.fh[self.counter][3] > self.p4high:
                self.p4date = self.fh[self.counter][0]
                self.p4high = self.fh[self.counter][3]
                self.p4arrow = True
                self.p24line = True
                self.incriment = False
                self.textbox.setText('Point 4 set at %.2f'%self.p4high)
            else:
                self.textbox.setText('New data did nothing')
                self.nodata = True
                self.incriment = True

        self.on_draw()

    
    def on_draw(self):
        """ Redraws the figure
        """
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        

        diff = self.fh[-1][0] - self.fh[0][0]

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
            self.axes.annotate('Start', xy=(self.fh[self.counter-30][0],self.fh[self.counter-30][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->")) 
            self.axes.annotate('End', xy=(self.fh[self.counter][0],self.fh[self.counter][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))         

        if self.p1arrow and self.boolUP:
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1high), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolUP:
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolUP:
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3high), xytext=(-10,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolUP:
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             

        if self.p1arrow and self.boolDOWN:
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1low), xytext=(-10,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow and self.boolDOWN:
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow and self.boolDOWN:
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3low), xytext=(-10,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow and self.boolDOWN:
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4high), xytext=(0,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             

        if self.p13line and self.boolUP:
            line1 = Line2D(xdata=[self.p1date,self.p3date], ydata=[self.p1high,self.p3high],color='b',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)
        if self.p24line and self.boolUP:
            line1 = Line2D(xdata=[self.p2date,self.p4date], ydata=[self.p2low,self.p4low],color='r',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)

        if self.p13line and self.boolDOWN:
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

        if self.p24line:
            self.boolUP = False
            self.boolDOWN = False

        if self.incriment:
            self.counter += 1
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 7x6 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((7.0, 7.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Other GUI controls
        # 
        self.stockbox = QLineEdit()
        self.stockbox.setMinimumWidth(100)
        self.stockbox.setMaximumWidth(100)

        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.get_stock)
        
        self.draw_button = QPushButton("&Next")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.trend)
        
        self.stockbutton = QPushButton("&Get Stock")
        self.connect(self.stockbutton, SIGNAL('clicked()'), self.get_stock)

        self.triangle_up = QCheckBox("Triangle")
        self.triangle_up.setChecked(True)
        self.connect(self.triangle_up, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.headandshoulders = QCheckBox("Head and Shoulders")
        self.headandshoulders.setChecked(False)
        self.connect(self.headandshoulders, SIGNAL('stateChanged(int)'), self.on_draw)

        slider_label = QLabel('Percent of Trend (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(55)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)

        self.firstdatebox = QDateEdit()
        self.lastdatebox = QDateEdit()

        self.firstdatebox.setDisplayFormat('MM/yyyy')
        self.lastdatebox.setDisplayFormat('MM/yyyy')
        self.firstdatebox.setDate(QDate.fromString('012006', 'MMyyyy'))
        self.lastdatebox.setDate(QDate.fromString('072009', 'MMyyyy'))

        self.datebutton = QPushButton("&Change Dates")
        self.connect(self.datebutton, SIGNAL('clicked()'), self.change_dates)
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        hbox15 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        
        for w in [  self.stockbox, self.stockbutton, self.firstdatebox, self.lastdatebox, self.datebutton ]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
            
        for y in [ self.triangle_up, self.headandshoulders ]:
            hbox15.addWidget(y)
            hbox15.setAlignment(y, Qt.AlignVCenter)

        for x in [ self.textbox, self.draw_button ]:
            hbox2.addWidget(x)
            hbox2.setAlignment(x, Qt.AlignVCenter)
        
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox15)
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
