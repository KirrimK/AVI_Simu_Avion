from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from IvyCom import IvyRadio
from backendManche import MancheRadio

class Window(QMainWindow):
    def __init__(self,radio):
        super().__init__()
        self.resize(1200, 600)
        self.setWindowTitle("Contrôles des sufarces de vol")
        self.radio = IvyRadio()
        self.manche = MancheRadio(self)
        self.setupSliders ()
        self.pBrut = 0
        self.nzBrut = 0
    def setupSliders (self):
        pass