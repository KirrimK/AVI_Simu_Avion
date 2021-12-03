from ivy.std_api import IvyStart, IvyStop, IvyInit, IvyBindMsg, IvySendMsg
class IvyRadio ():
    def  __init__ (self):
        self.nom = 'MiniManche'
        IvyInit (self.nom,self.nom+" is ready!")
        self.bus = "127.255.255.255:2010"
        #Messages à recevoir :
        self.btnPousse = "^FCUAP1 push$"
        self.vecteurDEtat = "^StateVector x=(.+) y=(.+) z=(.+) Vp=(.+) fpa=(.+) psi=(.+) phi=(.+)$"
        self.commandeAutoPilote = "^AutoPilot nx=(.+) nz=(.+) rollRate=(.+)$"
        #Messages à envoyer : 
        self.infoLimites = "MM Limites vMin={} vMax={} phiLim={} nxMin={} nxMax={} nzMin={} nzMax={} pLim={}"
        self.commandeVitesse = "MM Vc={}"
        self.FCUAP = "FCUAP {}"
        self.commandeModeleNx = "APNxControl nx={}"
        self.commandeModeleNx = "APNzControl nz={}"
        self.commandeModelep = "APLatControl rollRate={}"

        IvyBindMsg (self.onBoutonAPPush, self.btnPousse)
        IvyBindMsg (self.onRcvStateVector, self.vecteurDEtat)
        IvyBindMsg (self.onRcvAPCommand, self.commandeAutoPilote)

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
    def onBoutonAPPush (self,sender):
        """Fonction appelée par un callback d'un message de l'interface.
        Broadcast la valeur allumée ou éteinte du pilote automatique."""
        #Traitement
        self.sendAPState()
    def onRcvStateVector (self,sender,x,y,z,Vp,fpa,psi,phi):
        """Fonction appelée par un callback d'un message de l'interface.
        Les valeurs sont utilisées pour calculer les limites de commande."""
        pass
    def onRcvAPCommand (self,sender,nx, nz, p):
        """Fonction appelée par une callback de message pilote automatique.
        Appelle l'envoie des valeurs approuvées par les limites de l'avion."""
        pass
        #Envoi de messages
    def sendSpeedCommand (self, Vc):
        """Envoie une commande de vitesse managée à l'auto pilote."""
        self.sendMessage

    def sendAPState(self):
        """Envoie l'état de l'auto pilote."""
        état = getAPState ()
        self.sendMessage(self.FCUAP.format(état))

    def sendAircraftCommand (self,nx,nz,p):
        """Envoie les commandes de vol au modèle d'avion."""
        self.sendMessage (self.commandeModeleNx.format(nx))
        self.sendMessage (self.commandeModeleNz.format(nz))
        self.sendMessage (self.commandeModelep.format (p))

    def sendLimitsInfo (self, vMin, vMax, phiLim, nxMin, nxMax, nzMin, nzMax, pLim):
        self.sendMessage(self.infoLimites.format(vMin, vMax, phiLim, nxMin, nxMax, nzMin, nzMax, pLim))
