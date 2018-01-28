import sys
import time
import socket
import os
import main
import signal
from multiprocessing import Process

#from PyQt4.QtWidgets import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
class ChildWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.state = 0 # 0 for disconnect 1 for connecting 2 for connected
        #help(self)

    @pyqtSlot()
    def on_click(self):
        if self.state==0:
            self.status.setText('Connecting...')
            self.status.setStyleSheet("color: rgb(255, 165, 0);")
            self.button.setText('Disconnect')
            self.emit(SIGNAL('start_conn()'))
        if self.state==1:
            pass
        if self.state==2:
            self.status.setText('Disconnecting...')
            self.status.setStyleSheet("color: rgb(255, 165, 0);")
            self.button.setText('Connect')
            self.emit(SIGNAL('end_conn()'))



    def conn_success(self):
        self.state = 2
        self.status.setText('Connected')
        self.status.setStyleSheet("color: rgb(50, 205, 0);")

    def conn_failed(self):
        self.state = 0
        self.status.setText('Disconnected')
        self.status.setStyleSheet("color: rgb(255, 0, 0);")

    def startb(self, rec, loc, dst, passwd):
        self.backend = BackEnd(self, rec, loc, dst, passwd)
        self.backend.start()
        self.connect(self.backend, SIGNAL('conn_success()'), self.conn_success)
        self.connect(self.backend, SIGNAL('conn_failed()'), self.conn_failed)


class BackEnd(QThread):

    def __init__(self, parent, rec, loc, dst, passwd):
        QThread.__init__(self)
        self.rec = rec
        self.loc = loc
        self.dst = dst
        self.passwd = passwd
        self.connect(parent, SIGNAL('start_conn()'), self.start_conn)
        self.connect(parent, SIGNAL('end_conn()'), self.end_conn)
        self.proc = None

    def __del__(self):
        self.wait()

    def run(self):
        x = 0
        while True:
            sock = socket.socket()
            sock.settimeout(10)
            err = sock.connect_ex((self.dst,8099)) # Just a random port
            print(err)
            # if err:
            #     print('hey')
            self.emit(SIGNAL('conn_success()'))
            # else:
            #     # self.emit(SIGNAL('conn_failed()'))
            #     # os.kill(self.proc.pid, signal.SIGKILL)
            #     pass
                
            time.sleep(60)

    def start_conn(self):
        print('Initialising connection')
        self.proc = Process(target=main.start_main, args=(self.rec, self.loc, self.dst, self.passwd, 'socialtun'))
        self.proc.start()

    def end_conn(self):
        print('Killing connection')
        self.emit(SIGNAL('conn_failed()'))
        os.kill(self.proc.pid, signal.SIGKILL)
        self.proc = None
        #self.emit(SIGNAL('conn_success()'))

class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'Whatsapp VPN'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 250
        self.font = QFont()
        self.font.setBold(True)
        self.child_window = ChildWindow()

        self.initUI()
    def initChild(self):
        self.child_window.setWindowTitle('Child window')
        self.child_window.resize(240, 300)
        self.child_window.top = 100
        self.child_window.left = 100
        self.child_window.user_label = QLabel("Status:", self.child_window)
        self.child_window.user_label.move(20, 25)
        self.child_window.status = QLabel("Disconnected", self.child_window)
        self.child_window.status.move(90, 25)
        self.child_window.status.setFont(self.font)
        self.child_window.status.setStyleSheet("color: rgb(255, 0, 0);")
        self.child_window.button = QPushButton('Connect', self.child_window)
        self.child_window.button.move(80, 230)
        self.child_window.button.clicked.connect(self.child_window.on_click)


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.user_label = QLabel("Receipient:", self)
        self.user_label.move(20, 25)
        self.user_label = QLabel("Local IP:", self)
        self.user_label.move(20, 70)
        self.user_label = QLabel("Dest IP:", self)
        self.user_label.move(20, 110)
        self.user_label = QLabel("Password:", self)
        self.user_label.move(20, 140)
        # Create textbox


        self.receipient = QLineEdit(self)
        self.receipient.move(100, 25)
        self.receipient.resize(280,30)

        self.destip = QLineEdit(self)
        self.destip.move(100, 70)
        self.destip.resize(280,30)

        self.localip = QLineEdit(self)
        self.localip.move(100, 110)
        self.localip.resize(280,30)

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.move(100, 145)
        self.password.resize(280,30)

        # Create a button in the window
        self.button = QPushButton('Login', self)
        self.button.move(280,190)
 
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)

        # Child
        self.initChild()


        self.show()

 
    @pyqtSlot()
    def on_click(self):
        receipient = self.receipient.text()
        destip = self.destip.text()
        localip = self.localip.text()
        password = self.password.text()
        self.child_window.startb(receipient, destip, localip, password)
        self.child_window.show()
        # QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        # self.textbox.setText("")



 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
