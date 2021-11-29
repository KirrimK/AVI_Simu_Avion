from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
class IvyRadio ():
    def  __innit__ (self):
        self.nom = 'MiniManche'
        IvyInit (self.nom,self.nom+" is ready!")
        self.bus = "127.255.255.255:2010"
        #Messages à recevoir :
        self.btnPousse = "^FCUAP1 push$"
        self.vecteurDEtat = "^StateVector x=(.+) y=(.+) z=(.+) Vp=(.+) fpa=(.+) psi=(.+) phi=(.+)$"
        self.commandeAutoPilote = "^AutoPilot nx=(.+) nz=(.+) rollRate=(.+)$"
        #Messages à envoyer : 
        self.commandeVitesse = "MM Vc={}"
        self.FCUAP = "FCUAP {}"
        self.commandeModeleNx = "APNxControl nx={}"
        self.commandeModeleNx = "APNzControl nz={}"
        self.commandeModelep = "APLatControl rollRate={}"

        IvyBindMsg (self.onBoutonAPPush, self.btnPousse)
        IvyBindMsg (self.onRcvStateVector, self.vecteurDEtat)
        IvyBindMsg (self.onRcvAPCommand, self.commandeAutoPilote)

    def startRadio (self):
        IvyStart (self.bus)
    def stopRadio (self):
        IvyStop()
    def sendMessage (self, message):
        IvySendMsg(message)

        #Réactions aux messages
    def onBoutonAPPush (self,sender):
        #Traitement
        self.sendAPState()
    def onRcvStateVector (self,sender,x,y,z,Vp,fpa,psi,phi):
        pass
    def onRcvAPCommand (self,sender,nx, nz, p):
        """Fonction appelée par une callback de message pilote automatique"""
        pass
        #Envoi de messages
    def sendSpeedCommand (self, Vc):
        """Envoie une commande de vitesse managée à l'autilote."""
        self.sendMessage

    def sendAPState(self):
        """Envoie l'état de l'autopilote."""
        état = getAPState ()
        self.sendMessage(self.FCUAP.format(état))

    def sendAircraftCommand (self,nx,nz,p):
        """Envoie les commandes de vol au modèle d'avion."""
        self.sendMessage (self.commandeModeleNx.format(nx))
        self.sendMessage (self.commandeModeleNz.format(nz))
        self.sendMessage (self.commandeModelep.format (p))
