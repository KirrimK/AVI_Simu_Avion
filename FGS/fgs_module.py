# FGS_module

from ivy.std_api import *
import time
import math

STATEVEC_REGEX = "StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)"
#WINDCOMP_REGEX = "WindComponent VWind=(\S+) dirWind=(\S+)"
#DM_REGEX = "MagneticDeclination MagneticDeclination=(\S+)"
DIRTO_REGEX = "DIRTO Wpt=(\S+)"
TIMESTART_REGEX = "Time t=1.0"
LIMITES_REGEX = "MM Limites vMin=(\S+) vMax=(\S+) phiLim=(\S+) nxMin=(\S+) nxMax=(\S+) nzMin=(\S+) nzMax=(\S+) pLim=(\S+)"

TARGET_MSG = "Target X={} Y={} Z={} Khi={}"

FLYBY = "flyBy"
OVERFLY = "overFly"

KTS2MS = 0.5144447
DEG2RAD = 0.01745329

InitStateVector=[0, 0, 0, 214*KTS2MS, 0, 0, 0] #la vitesse de décollage est de 110 m/s


class Waypoint:
    """
    Objet contenant les informations d'un Waypoint
    """
    def __init__(self, name, x, y, z, mode):
        self.nom = name #string
        self.x = x #float
        self.y = y #float
        self.z = z #float
        self.mode = mode #string: "overFly" | "flyBy"

    def name(self):
        return self.nom

    def infos(self):
        return (self.nom, self.x, self.y, self.z, self.mode)

def load_flight_plan(filename):
    """Retourne une liste de Waypoints (un PDV) depuis un fichier
    Arguments: filename: string
    Retourne: flight_plan: Waypoint list
    """
    listWpt = []
    with open(filename,"r") as f:
        for ligne in f:
            list = ligne.split()
            listWpt.append(Waypoint(list[0],list[1],list[2],list[3],list[4]))
    return listWpt 

class FGS:
    """
    L'objet contenant toutes les fonctions et variables du FGS
    """

    def __init__(self, filename, vwind, dirwind, MagneticDeclination):
        """Constructeur du FGS
        Arguments:
            - filename: string
        """
        self.dirto_on = False
        self.dirto_target_number = 0
        self.phi_max = 0 #radians
        self.flight_plan = load_flight_plan(filename)
        self.current_target_on_plan = 0
        self.lastsenttarget = (0, 0, 0, 0)
        self.targetmode = FLYBY
        self.vwind = vwind 
        self.dirwind = dirwind
        self.dm = MagneticDeclination
        self.state_vector = InitStateVector.copy()
        IvyBindMsg(self.on_state_vector, STATEVEC_REGEX)
        IvyBindMsg(self.on_dirto, DIRTO_REGEX)
        IvyBindMsg(self.on_time_start, TIMESTART_REGEX)
        IvyBindMsg(self.on_limit_msg, LIMITES_REGEX)

    def on_state_vector(self, sender, *data):
        """Callback de StateVector
        Entrée Ivy:
            - x, y, z, vp, fpa, psi, phi: floats
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        pass
        #mettre à jour les infos connues sur l'avion (unpack data)
        
        if self.dirto_on:
            #Séquençage
            
            #Envoyer la prochaine target
            IvySendMsg("Waypoint".format())
        
        #Sinon
        else:
            #si wpt a été dépassé (overFly)
            if Waypoint.mode == "overFly":
                #envoyer dirtorequest
                IvySendMsg("DirtoRequest")

                #continuer à envoyer la même target tant que pas de nv dirto

            #sinon
            else:
                #envoyer la même requête qui a été générée lors de la réception du dirto
                IvySendMsg()


    def on_dirto(self, sender, *data):
        """Callback de DIRTO
        Entrée Ivy: WptName: string
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        #pas de dirto sur un pt du pdv déjà séquencé
        #le dirto est un raccourci dans le PDV
        #dirto flyby par défaut
        (dirto_wpt) = data
        #chercher le WPT dans la liste des WPTs non séquencés, via recherche linéaire
        for i in range(self.current_target_on_plan, len(self.flight_plan)):
            if self.flight_plan[i].name() == dirto_wpt:
                #get les infos du Wpt
                _, x_wpt, y_wpt, z_wpt, wpt_mode = self.flight_plan[i].infos()
                #calculer la direction à mettre
                route = math.atan2(y_wpt-self.state_vector[1], x_wpt-self.state_vector[0])
                #trouver la prochaine contrainte d'altitude, si il n'y en a pas, garder la plus récente
                contrainte = -1
                found_next = False
                for j in range(i, len(self.flight_plan)):
                    if self.flight_plan[j].infos()[3] != -1:
                        contrainte = self.flight_plan[j].infos()[3]
                        break
                if not found_next:
                    contrainte = self.lastsenttarget[2]
                #sauvegarder le message à envoyer
                self.lastsenttarget = (x_wpt, y_wpt, contrainte, route)
                self.targetmode = FLYBY
                #mettre à jour le numéro de la target en cours
                self.current_target_on_plan = i
                #activer le mode dirto
                self.dirto_on = True
                #envoyer le 1er msg
                IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
                break
        

    def on_time_start(self, sender, *data):
        """Callback de Time t=0.0
        Entrée Ivy: Rien
        Sortie Ivy: 3 messages sur Ivy
            - InitStateVector
            - WindComponent
            - MagneticDeclination
        """
        IvySendMsg("StateVector x={} y={} z={} Vp={} fpa={} psi={} phi={}".format(*InitStateVector))
        IvySendMsg("WindComponent VWind={} dirWind={}".format(self.vwind,self.dirwind))
        IvySendMsg("MagneticDeclination MagneticDeclination={}".format(self.dm))


    def on_limit_msg(self, sender, *data):
        """Retourne une liste de Waypoints (un PDV) depuis un fichier
        Entrée Ivy: (Message de limites)
        Sortie: Met à jour le phi max en mémoire
        """
        _, _, recv_str_phi, _, _, _, _, _ = data
        self.phi_max = float(recv_str_phi)


if __name__=="__main__":
    IvyInit("FGS", "Ready")
    IvyStart("10.1.127.255:2010") #IP à changer
    time.sleep(1.0)
    fgs = FGS("pdv.txt")

##### Pour référence future #####
#IvySendMsg("")
#IvyBindMsg(callback, "regex")

#def generic_callback(sender, *data):
#    pass
