from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from IvyCom import IvyRadio
from backendManche import MancheRadio
from limites2 import Avion
from jukebox import Jukebox

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
        self.bruitages = Jukebox()
        self.radio.qtEmetteur.BoutonPousseSignal.connect (self.onButtonPushSignal)
        self.radio.qtEmetteur.VecteurDEtatSignal.connect (self.onVecteurDEtatSignal)
        self.radio.qtEmetteur.CommandeAPSignal.connect (self.onCommandeAPSignal)
        print ("Ready\n")

    def setupSliders (self):
        layout = QHBoxLayout()
        self.setLayout (layout)
        self.sliderTrainAtt = QSlider (Qt.Vertical)
        self.sliderTrainAtt.setMinimum (0)
        self.sliderTrainAtt.setMaximum (1)
        self.sliderTrainAtt.setTickInterval (1)
        self.sliderTrainAtt.setValue(1)
        self.sliderTrainAtt.show()
        layout.addWidget (self.sliderTrainAtt)
        self.sliderTrainAtt.valueChanged.connect (self.onSliderValueChanged)

        self.sliderFlaps = QSlider (Qt.Vertical)
        self.sliderFlaps.setMaximum (4)
        self.sliderFlaps.setMinimum (0)
        self.sliderFlaps.setValue (1)
        layout.addWidget(self.sliderFlaps)
        self.sliderFlaps.valueChanged.connect (self.onSliderValueChanged)
        
        self.sliderFlaps.setTickInterval (1)
        self.sliderFlaps.show ()

    def onSliderValueChanged (self):
        self.avion.update_sliders(self.sliderFlaps.value(),self.sliderTrainAtt.value())

    def onButtonPushSignal (self,forceOff):
        arme = self.isAPOn
        if forceOff:
            self.isAPOn = False
        elif (not self.isAPOn) and True:
            self.isAPOn = True
        else :
            self.isAPOn = False
        if arme and not self.isAPOn:
            self.bruitages.shutdownPA()
        self.radio.sendAPState(self.isAPOn)
        
    def onVecteurDEtatSignal (self,argTuple):
        (x,y,alt,V,gamma,psi,phi) = argTuple
        if V>self.avion.vitesse_lim:
            self.bruitages.overSpeeed ()
        if alt <50 and not self.avion.train:
            self.bruitages.pulllUp()
        self.avion.reception_vecteur_etat (alt,V,gamma,phi)
        self.radio.sendSpeedCommand (self.avion.vitesse_i)

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
            if nzCons >nzMax:
                nzCons = 1
        elif self.nzBrut <-0.1:
            nzCons = 1 - (self.nzBrut)/(nzMin -1)
            if nzCons < nzMin :
                nzCons = 1
        else : 
            nzCons = 1
        if self.pBrut<-0.1 or self.pBrut >0.1:
            pCons = 15 * 3.141592654 /180 * self.pBrut
            if self.avion.p_lim [0]> pCons or self.avion.p_lim[1]<pCons:
                pCons = 0
        else :
            pCons = 0
        return (nzCons,pCons)
