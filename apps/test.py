import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.finance as finance
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter, DayLocator, MONDAY, WeekdayLocator

import MySQLdb

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.setup_dbase()
        self.setup_trend()
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.textbox.setText('Press Next to Start Looking for Trend')
        self.on_draw()

    def setup_dbase(self):
        self.ticker = 'GOOG'
        self.db = MySQLdb.connect(host='166.70.159.134', user='nick', passwd='mohair94', db='market')
        self.curs = self.db.cursor()

        query="""SELECT date,open,close,high,low,volume from %s order by date"""%self.ticker
#        query="""SELECT date,open,close,high,low,volume from %s where date > 733480 AND date < 733575 order by date"""%self.ticker
        self.curs.execute(query)
        
        self.fh = self.curs.fetchall()

    def setup_trend(self):
        self.counter = 30
        self.pot = 30.0
        self.lastDay = self.fh[0]
        self.boolUP = False
        self.boolDOWN = False
        self.line1 = None
        self.p1date = 0
        self.p1high = 0
        self.p1low = 0
        self.p2date = 0
        self.p2low = 0
        self.p3date = 0
        self.p3high = 0
        self.p4date = 0
        self.p4low = 0
        self.diff = 0
        self.incriment = False
        self.p1arrow = False
        self.p2arrow = False
        self.p3arrow = False
        self.p4arrow = False
        self.trendline = True
        self.p13line = False
        self.p24line = False

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
        self.diff = 0
            
        if changeUP > 55 and not self.boolUP:
            self.textbox.setText('Upward trend identified. Point 1 set at %.2f'%self.fh[self.counter][3])
            self.boolUP = True
            self.incriment = True
            self.trendline = False
            self.p1arrow = True
        elif changeDOWN > 55 and not self.boolDOWN:
            self.textbox.setText('Downward trend identified')
            self.boolDOWN = True
            self.incirment = True
        else:
            self.textbox.setText('No trend identified')
            self.incriment = True

    def trend(self):
        if not self.boolUP and not self.boolDOWN:
            self.identify_trend()
        elif self.boolUP or self.boolDOWN:
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
                self.incriment = True
                self.boolUP = False
                self.boolDOWN = False
                self.textbox.setText('Point 4 set at %.2f'%self.p4low)
            else:
                self.textbox.setText('New data did nothing')
                

        self.on_draw()


    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
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
    
    def on_draw(self):
        """ Redraws the figure
        """
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        

        finance.candlestick(self.axes, quotes=self.fh[0:99], width=0.4, colorup='green', colordown='red')

#        if self.line1:
#            self.axes.add_line(self.line1)
        if self.trendline:
            self.axes.annotate('Start', xy=(self.fh[self.counter-30][0],self.fh[self.counter-30][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->")) 
            self.axes.annotate('End', xy=(self.fh[self.counter][0],self.fh[self.counter][3]), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))         
        if self.p1arrow:
            self.axes.annotate('Point 1', xy=(self.p1date,self.p1high), xytext=(-50,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p2arrow:
            self.axes.annotate('Point 2', xy=(self.p2date,self.p2low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p3arrow:
            self.axes.annotate('Point 3', xy=(self.p3date,self.p3high), xytext=(-10,30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p4arrow:
            self.axes.annotate('Point 4', xy=(self.p4date,self.p4low), xytext=(0,-30), xycoords='data', textcoords='offset points',arrowprops=dict(arrowstyle="->"))             
        if self.p13line:
            line1 = Line2D(xdata=[self.p1date,self.p3date], ydata=[self.p1high,self.p3high],color='b',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)
        if self.p24line:
            line1 = Line2D(xdata=[self.p2date,self.p4date], ydata=[self.p2low,self.p4low],color='r',linewidth=1.0,antialiased=True,)        
            self.axes.add_line(line1)

        self.axes.set_title('%s Daily'%self.ticker)
        self.axes.xaxis.set_major_locator(WeekdayLocator(MONDAY)) # major ticks on the mondays
        self.axes.xaxis.set_minor_locator(DayLocator()) # minor ticks on the days
        self.axes.xaxis.set_major_formatter(DateFormatter('%b %d')) # Eg, Jan 12
        #self.axes.xaxis.set_major_formatter(DateFormatter('%d') # Eg, 12
        self.axes.xaxis_date()
        #self.axes.autoscale_view()
        for label in self.axes.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')
        self.axes.grid()

        self.canvas.draw()

        if self.incriment:
            self.counter += 1
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 7x6 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((7.0, 6.0), dpi=self.dpi)
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
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
        
        self.draw_button = QPushButton("&Next")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.trend)
        
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
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        
        for w in [  self.textbox, self.draw_button]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        for x in [ self.slider ]:
            hbox2.addWidget(x)
            hbox.setAlignment(x, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
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
