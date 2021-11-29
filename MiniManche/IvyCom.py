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
        self.FCUAP = "FCUAP {}"
        self.commandeModele = "APNxControl nx={}\nAPNzControl nz={}\nAPLatControl rollRate"

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
        pass
        #Envoi de messages
    def sendAPState(self):
        état = getAPState ()
        self.sendMessage(self.FCUAP.format(état))
    def sendAircraftCommand (self,nx,nz,p):
        self.sendMessage (self.commandeModele.format(nx,nz,p))
