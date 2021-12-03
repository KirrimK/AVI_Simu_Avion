# FGS_module

from ivy.std_api import *
import time

STATEVEC_REGEX = "StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)"
DIRTO_REGEX = "DIRTO Wpt=(\S+)"
TIMESTART_REGEX = "Time t=1.0"
LIMITES_REGEX = "MM Limites vMin=(\S+) vMax=(\S+) phiLim=(\S+) nxMin=(\S+) nxMax=(\S+) nzMin=(\S+) nzMax=(\S+) pLim=(\S+)"

InitStateVector=[0,0,0,110,0,0,0] #la vitesse de décollage est de 110 m/s

class Waypoint:
    """
    Objet contenant les informations d'un Waypoint
    """
    def __init__(self, name, x, y, z, mode):
        self.name = name #string
        self.x = x #float
        self.y = y #float
        self.z = z #float
        self.mode = mode #string: "overFly" | "flyBy"

    def infos(self):
        return (self.name, self.x, self.y, self.z, self.mode)

def load_flight_plan(filename):
    """Retourne une liste de Waypoints (un PDV) depuis un fichier
    Arguments: filename: string
    Retourne: flight_plan: Waypoint list
    """
    listWpt = []
    with open(filename,"r") as f:
        for ligne in f:
            listWpt.append(ligne.split())
    return listWpt 

class FGS:
    """
    L'objet contenant toutes les fonctions et variables du FGS
    """

    def __init__(self, filename):
        """Constructeur du FGS
        Arguments:
            - filename: string
        """
        self.dirto_on = False
        self.phi_max = 0 #radians
        self.flight_plan = load_flight_plan(filename)
        self.currenttarget = 0
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

    def on_dirto(self, sender, *data):
        """Callback de DIRTO
        Entrée Ivy: WptName: string
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        pass

    def on_time_start(self, sender, *data):
        """Callback de Time t=0.0
        Entrée Ivy: Rien
        Sortie Ivy: 3 messages sur Ivy
            - InitStateVector
            - WindComponent
            - MagneticDeclination
        """
        pass

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
