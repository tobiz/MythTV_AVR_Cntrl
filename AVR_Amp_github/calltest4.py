import sys
import subprocess
import ipaddress

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QDialogButtonBox,  QPushButton, QProgressBar
from PyQt5 import QtCore, QtGui, QtWidgets,  uic
from PyQt5.QtCore import QDate, Qt, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QObject, QSize


from MarantzAPI3 import *
from hid_API import *
import resources



#qtcreator_file  = "test2.ui" # Enter file here.
#qtcreator_file  = "/home/pjr/Development/AVR_Amp/test2.ui" # Enter file here.
qtcreator_file  = "/home/pjr/Development/AVR_Amp/test6.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

qtresources_file = "/home/pjr/Development/AVR_Amp/resources.qrc"
#Ui_Resources, 

# tag::WorkerSignals[]
class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)

# tag::Worker[]
class Worker(QRunnable):
    """
    Worker thread
    """
    def __init__(self, button):
	    	super().__init__()
	    	self.signals = WorkerSignals()
	    	self.button = button
	    	
    def setdata(self, cmds, state):
    	self.cmds = cmds
    	self.state = state
	 
	 #def setdata(self, cmds, state):
	 #		self.cmds = cmds
	 #		self.state = state
	    	

    @pyqtSlot()
    def run(self):
        #
        # Executes the commands to control the AV Amp and the central Speaker control relay
        #	Commands in the form [ [cmd_type, cmd]...] where:
        #	cmd_type is write|amp, cmd is actual command
        #	eg cmds == [["write", "PWON"], ["amp", "Surround Back"], ["write, "PSFRONT SPA"], ["write", "PWSTANDBY"]] 
        #
        print("Thread start")
        self.avr = IP( 23, 1, av_url="192.168.1.20", browser="firefox")
        for cmd in self.cmds:
	        #print("cmd type: ", cmd[0], ", cmd: ", cmd[1])
	        #continue
	        if cmd[0] == "write":
	        	self.avr.write_command(cmd[1])
	        if cmd[0] == "amp":
	        	self.avr.amp_assign(cmd[1])
	     # Change relay state to control central speaker   	
        p = subprocess.run(["python3", "/home/pjr/Development/AVR_Amp/hidcall_py2.py", "1", self.state])
        #self.signals.finished.emit()
        self.signals.error.emit(self.button)
        print("Thread complete")

class mythAVAmp_cntrl(QMainWindow, Ui_MainWindow):
	#def __init__(self):
	def __init__(self, x=196, y=173, w=1000, h=800):
		QtWidgets.QMainWindow.__init__(self)
		
		self.x = int(x)
		self.y = int(y)
		self.w = int(w)
		self.h = int(h)
		print("x=%i, y=%i, w=%i, h=%i\n" % (self.x, self.y, self.w, self.h))
		
		#QtWidgets.QMainWindow.__init__(self).setFixedSize(QSize(self.w, self.h))
		Ui_MainWindow.__init__(self)
		super().__init__()
		self.date = QDate.currentDate()
		self.setupUi(self) 
		#self.setFixedSize(QSize(self.w, self.h))
		#setFixedSize(QSize(self.w, self.h))
		self.initUI()
		
		
		


	def initUI(self):
			
			self.ui = Ui_MainWindow()
			self.ui.setupUi(self)
			self.ui.SpeakerTVPushButton.clicked.connect(self.TVClicked)
			self.ui.SpeakerLoungePushButton.clicked.connect(self.LoungeClicked)
			self.ui.AVAMP_IP.returnPressed.connect(self.AVAMP_IP_Clicked)
			self.ui.ExitbuttonBox.accepted.connect(self.close)
			self.ui.BrowserType.currentIndexChanged.connect(self.browser_type)
			self.statusBar().showMessage(self.date.toString(Qt.DefaultLocaleLongDate))
			self.setWindowTitle('MythTV AV Amp Control')
			
			self.threadpool = QThreadPool()
			#print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
			
			self.IP_Addr = ""
			self.TV_bgc = "Blue"
			self.L_bgc = "Blue"
			      	
			self.show()
			
			
	def browser_type(self):
		self.browser = self.ui.BrowserType.itemText(self.ui.BrowserType.currentIndex())
		print ("Browser type is: ", self.browser)
		
	def TVClicked(self):
		print ("Speaker TV Button clicked")
		self.ui.progressBar.setMaximum(0)
		self.ui.progressBar.setFormat("Speaker Config End")
		self.worker = Worker("TV")
		#self.worker.signals.finished.connect(self.worker_complete)
		self.worker.signals.error.connect(self.worker_complete)
		self.worker.setdata([["write", "PWON"], ["amp", "Surround Back"], ["write", "PSFRONT SPA"], ["write", "PWSTANDBY"]], "on")
		self.threadpool.start(self.worker)
		print("Speakers config TV")
		
	def worker_complete(self, button):
		#print("worker_complete called by: ", button)
		if button == "TV":
			self.ui.SpeakerTVPushButton.setStyleSheet("background-color : green")
			self.ui.SpeakerLoungePushButton.setStyleSheet("background-color : blue")
		if button == "L":
			self.ui.SpeakerLoungePushButton.setStyleSheet("background-color : green")
			self.ui.SpeakerTVPushButton.setStyleSheet("background-color : blue")
			
		# Accepts the "finished" signal from the Worker thread and stops the progressbar pulse
		self.ui.progressBar.setMaximum(100)
		
				
				        
	def LoungeClicked(self):
		print ("Speaker Lounge Button clicked")
		self.ui.progressBar.setMaximum(0)			# Set progressbar pulsing
		self.ui.progressBar.setFormat("Speaker Config End")
		self.worker = Worker("L")
		self.worker.signals.error.connect(self.worker_complete)
		self.worker.setdata([["write", "PWON"], ["amp", "ZONE2"], ["write", "PWSTANDBY"]], "off")
		self.threadpool.start(self.worker)
		print("Speakers config Lounge")
		
		return
            
	def AVAMP_Browser_Clicked(self):
		self.Browser = self.ui.AVAMP_Browser.text()
		if self.Browser == "":
			print ("Supply Browser Type")
		print ("AVAMP_Browser_Clicked. Value is: ", self.ui.AVAMP_Browser.text())
    	      	  
              
	def AVAMP_IP_Clicked(self):
		self.IP_Addr = self.ui.AVAMP_IP.text()
		print ("AVAMP_IP_Clicked. Value is: ", self.IP_Addr)
		try:
			a = ipaddress.ip_address(self.IP_Addr)
		except ValueError:
			print ("For now - invalid IP address")
			self.ui.AVAMP_IP.setText("Invalid IP Addrs")
				
	def close(self):
		print("CLose Called OK")
		try:
			a = ipaddress.ip_address(self.IP_Addr)
		except ValueError:
			print ("For now - invalid IP address")
			self.ui.AVAMP_IP.setText("Invalid IP Addrs")
			return
		exit()

def main():

	app = QApplication(sys.argv)
	#w = mythAVAmp_cntrl()
	print ('Argument List:', str(sys.argv))
	w = mythAVAmp_cntrl(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	w.show()
	print ("Start Form")
	try:
		r = app.exec_()
	except :
		print("Exception")
		exit()
	print ("End Form")
	sys.exit()


if __name__ == '__main__':
	main()
