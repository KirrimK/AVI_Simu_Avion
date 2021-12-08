from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from IvyCom import IvyRadio
from backendManche import MancheRadio

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        #self.setWindowTitle("Contrôles des sufarces de vol")
        self.setupSliders ()

        self.radio = IvyRadio()
        self.manche = MancheRadio(self)
        self.manche.startThread()
        self.pBrut = 0
        self.nzBrut = 0
        self.isAPOn = True

    def setupSliders (self):
        layout = QHBoxLayout()
        self.setLayout (layout)

        self.sliderTrainAtt = QSlider (Qt.Vertical)
        self.sliderTrainAtt.setMinimum (0)
        self.sliderTrainAtt.setMaximum (1)
        self.sliderTrainAtt.setTickInterval (1)
        self.sliderTrainAtt.show()
        layout.addWidget (self.sliderTrainAtt)

        self.sliderFlaps = QSlider (Qt.Vertical)
        self.sliderFlaps.setMaximum (40)
        self.sliderFlaps.setMinimum (0)
        layout.addWidget(self.sliderFlaps)
        
        self.sliderFlaps.setTickInterval (10)
        self.sliderFlaps.show ()

    def onButtonPushSignal (self,boolManche):
        if boolManche:
            self.isAPOn = False
        elif (not self.isAPOn) and True:
            self.isAPOn = True
        else :
            self.isAPOn = False
        self.radio.sendAPState(self.isAPOn)
        
    def onVecteurDEtatSignal (self,argTuple):
        pass

    def onCommandeAPSignal (self,argTuple):
        (nX, nZ, p)=argTuple
        if self.isAPOn :
            # TODO vérification de limites 
            self.radio.sendAircraftCommand (nX, nZ, p)
        else :
            #TODO traitement des nz et p bruts
            #TODO limites à vérifier
            pass
