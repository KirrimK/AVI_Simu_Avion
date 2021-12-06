from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from IvyCom import IvyRadio
from backendManche import *

class Window(QMainWindow):
    def __init__(self,radio):
        super().__init__()
        self.resize(1200, 600)
        self.setWindowTitle("Contrôles des sufarces de vol")
        self.radio = 
        self.setupSliders ()
        self.axis0Brut = 0
        self.axis1Brut = 1
    def setupSliders (self):
        pass