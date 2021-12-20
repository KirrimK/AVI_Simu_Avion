from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout, QVBoxLayout
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
        layoutTrain = QVBoxLayout ()
        self.labelTr1 = QLabel ()
        self.labelTr1.setText ("Trains : Sortis")

        self.sliderTrainAtt = QSlider (Qt.Vertical)
        self.sliderTrainAtt.setMinimum (0)
        self.sliderTrainAtt.setMaximum (1)
        self.sliderTrainAtt.setTickInterval (1)
        self.sliderTrainAtt.setValue(0)
        self.sliderTrainAtt.show()
        layoutTrain.addWidget (self.sliderTrainAtt)
        layoutTrain.addWidget(self.labelTr1)
        layout.addLayout (layoutTrain)
        self.sliderTrainAtt.valueChanged.connect (self.onSliderValueChanged)

        layoutFlap = QVBoxLayout ()
        self.labelFlap = QLabel ()
        self.labelFlap.setText ("Flaps : configuration 1")

        self.sliderFlaps = QSlider (Qt.Vertical)
        self.sliderFlaps.setMaximum (4)
        self.sliderFlaps.setMinimum (0)
        self.sliderFlaps.setValue (3)
        layoutFlap.addWidget(self.sliderFlaps)
        layoutFlap.addWidget(self.labelFlap)
        layout.addLayout (layoutFlap)
        self.sliderFlaps.valueChanged.connect (self.onSliderValueChanged)
        
        self.sliderFlaps.setTickInterval (1)
        self.sliderFlaps.show ()

    def onSliderValueChanged (self):
        """Fonction appelée quand la valeur d'un des sliders est changée. Met à jour les labels 
        et le modèle d'avion (objet self.avion"""
        valeurFlap = 4-self.sliderFlaps.value()
        self.labelFlap.setText ("Flaps : configuration {}".format ("lisse" if valeurFlap == 0 else valeurFlap))
        

        trainValue = 1-self.sliderTrainAtt.value()
        self.labelTr1.setText ("Trains : {}".format("Sortis" if trainValue == 1 else "Rentrés"))
        self.avion.update_sliders(valeurFlap,trainValue)

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
        self.radio.sendLimitsInfo(self.avion.vitesse_lim,self.avion.phi_lim[1],self.avion.nx_lim[0],self.avion.nx_lim[1],self.avion.nz_lim[0],self.avion.nz_lim[1],self.avion.p_lim[1])

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
