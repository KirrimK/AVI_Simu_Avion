from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from IvyCom import IvyRadio
from backendManche import MancheRadio
from limites import Avion

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        #self.setWindowTitle("Contrôles des sufarces de vol")
        self.setupSliders ()

        self.radio = IvyRadio()
        self.manche = MancheRadio(self)
        self.avion = Avion (self)
        self.pBrut = 0
        self.nzBrut = 0
        self.isAPOn = True
        self.show()

    def setupSliders (self):
        layout = QHBoxLayout()
        self.setLayout (layout)
        self.labelTrain = QLabel ()
        self.labelTrain.setText ("Trains")
        self.sliderTrainAtt = QSlider (Qt.Vertical)
        self.sliderTrainAtt.setMinimum (0)
        self.sliderTrainAtt.setMaximum (1)
        self.sliderTrainAtt.setTickInterval (1)
        self.sliderTrainAtt.show()
        layout.addWidget (self.labelTrain)
        layout.addWidget (self.sliderTrainAtt)
        #self.sliderTrainAtt.valueChanged.connect TODO

        self.sliderFlaps = QSlider (Qt.Vertical)
        self.sliderFlaps.setMaximum (4)
        self.sliderFlaps.setMinimum (0)
        self.sliderFlaps.setValue (1)
        layout.addWidget(self.sliderFlaps)
        #self.sliderFlaps.valueChanged.connect TODO
        
        self.sliderFlaps.setTickInterval (1)
        self.sliderFlaps.show ()

    def onButtonPushSignal (self,forceOff):
        if forceOff:
            self.isAPOn = False
        elif (not self.isAPOn) and True:
            self.isAPOn = True
        else :
            self.isAPOn = False
        self.radio.sendAPState(self.isAPOn)
        
    def onVecteurDEtatSignal (self,argTuple):
        (x,y,alt,V,gamma,psi,phi) = argTuple
        self.avion.reception_vecteur_etat (alt,V,gamma,phi)

    def onCommandeAPSignal (self,argTuple):
        (nX, nZ, p)=argTuple
        if self.isAPOn :
            # TODO vérification de limites 
            self.radio.sendAircraftCommand (nX, nZ, p)
        else :
            (nZ,p)= self.traitement ()
            #TODO limites à vérifier
            self.radio.sendAircraftCommand (nX, nZ, p)

    def traitement (self):
        nzMin = -1
        nzMax = 2
        if self.nzBrut >0.1:
            nzCons = 1+(self.nzBrut)/(nzMax-1)
        elif self.nzBrut >-0.1:
            nzCons = 1 
        else : 
            nzCons = 1 - (self.nzBrut)/(nzMin -1)
        if self.pBrut<0.1 or self.pBrut >0.1:
            pCons = 15 * 3.141592654 /180
        else :
            pCons = 0
        return (nzCons,pCons)
