from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

class objetQt (QWidget):
    BoutonPousseSignal = pyqtSignal(bool)
    VecteurDEtatSignal = pyqtSignal (tuple)
    CommandeAPSignal = pyqtSignal (tuple)
    def __init__ (self):
        super().__init__()

class IvyRadio ():
    def  __init__ (self):
        self.nom = 'MiniManche'
        IvyInit (self.nom,self.nom+" is ready!")
        self.bus = "127.255.255.255:2010"
        #Messages à recevoir :
        self.btnPousse = "^FCUAP1 push$"
        self.vecteurDEtat = "^StateVector x=(.+) y=(.+) z=(.+) Vp=(.+) fpa=(.+) psi=(.+) phi=(.+)$"
        self.commandeAutoPilote = "^AutoPilot nx=(.+) nz=(.+) rollRate=(.+)$"
        self.initialMessage = "^InitStateVector"

        #Messages à envoyer : 
        self.infoLimites = "MM Limites vMin=0 vMax={} phiLim={} nxMin={} nxMax={} nzMin={} nzMax={} pLim={}"
        self.commandeVitesse = "MM VC={}"
        self.FCUAP = "FCUAP1 {}"
        self.commandeModeleNx = "APNxControl nx={}"
        self.commandeModeleNz = "APNzControl nz={}"
        self.commandeModelep = "APLatControl rollRate={}"
        self.qtEmetteur = objetQt ()
        IvyBindMsg (self.onMessage1, self.initialMessage)
        IvyBindMsg (self.onBoutonAPPush, self.btnPousse)
        IvyBindMsg (self.onRcvStateVector, self.vecteurDEtat)
        IvyBindMsg (self.onRcvAPCommand, self.commandeAutoPilote)
        self.startRadio ()

    def startRadio (self):
        """Fonction À APPELER IMPÉRATIVEMENT AU LANCEMENT DU PROGRAMME. Démarre la radio."""
        IvyStart (self.bus)

    def stopRadio (self):
        """Fonction À APPELER IMPÉRATIVEMENT À L'ARRÊT DU PROGRAMME. Enlève la radio du bus Ivy."""
        IvyStop()

    def sendMessage (self, message):
        """Fonction prenant une chaine de caractères et l'envoyant sur le bus Ivy """
        IvySendMsg(message)

        #Réactions aux messages
    def onMessage1 (self, *args):
        self.sendAPState(True)

    def onBoutonAPPush (self,sender,argManche = False):
        """Fonction appelée par un callback d'un message de l'interface ou par le manche."""
        if not argManche == True:
            argManche = False
        self.qtEmetteur.BoutonPousseSignal.emit(argManche)

    def onRcvStateVector (self,sender,x,y,z,Vp,fpa,psi,phi):
        """Fonction appelée par un callback d'un message de l'interface.
        Les valeurs sont utilisées pour calculer les limites de commande."""
        self.qtEmetteur.VecteurDEtatSignal.emit((float(x),float(y),float(z),float(Vp),float(fpa),float(psi),float(phi)))

    def onRcvAPCommand (self,sender,nx, nz, p):
        """Fonction appelée par une callback de message pilote automatique.
        Appelle l'envoie des valeurs approuvées par les limites de l'avion."""
        self.qtEmetteur.CommandeAPSignal.emit ((float(nx), float(nz), float(p)))

        #Envoi de messages
    def sendSpeedCommand (self, Vc):
        """Envoie une commande de vitesse managée à l'auto pilote."""
        self.sendMessage (self.commandeVitesse.format(Vc))

    def sendAPState(self,isOn):
        """Envoie l'état de l'auto pilote. 
        L'argument : isOn est un booléen qui donne l'état de l'AP1"""
        if isOn :
            self.sendMessage(self.FCUAP.format("on"))
        else : 
            self.sendMessage(self.FCUAP.format("off"))

    def sendAircraftCommand (self,nx,nz,p):
        """Envoie les commandes de vol au modèle d'avion."""
        self.sendMessage (self.commandeModeleNx.format(nx))
        self.sendMessage (self.commandeModeleNz.format(nz))
        self.sendMessage (self.commandeModelep.format (p))

    def sendLimitsInfo (self, vMax, phiLim, nxMin, nxMax, nzMin, nzMax, pLim):
        self.sendMessage(self.infoLimites.format(vMax, phiLim, nxMin, nxMax, nzMin, nzMax, pLim))
