from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider
from PyQt5.QtCore import pyqtSignal, Qt
from IvyCom import IvyRadio
from backendManche import MancheRadio

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        self.setWindowTitle("Contrôles des sufarces de vol")
        self.setupSliders ()

        self.radio = IvyRadio()
        self.manche = MancheRadio(self)
        self.pBrut = 0
        self.nzBrut = 0
    def setupSliders (self):
        pass
        sliderTrainAtt = QSlider (Qt.Vertical)
        sliderTrainAtt.setMinimum (0)
        sliderTrainAtt.setMaximum (1)
        sliderTrainAtt.setTickInterval (1)


        sliderFlaps = QSlider (Qt.Vertical)
        sliderFlaps.setTickInterval (10)
        sliderFlaps.setMaximum (40)
        sliderFlaps.setMinimum (0)

    def onButtonPushSignal (self,boolManche):
        pass
    def onVecteurDEtatSignal (self,argTuple):
        pass
    def onCommandeAPSignal (self,argTuple):
        pass

