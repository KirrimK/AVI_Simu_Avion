# FGS_module

from ivy.std_api import *
import time

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
    pass

class FGS:
    """
    L'objet contenant toutes les fonctions et variables du FGS
    """

    def __init__(self, filename):
        """Constructeur du FGS
        Arguments: filename: string
        """
        pass
        self.dirto_on = False
        self.flight_plan = load_flight_plan(filename)
        #register les callbacks

    def on_state_vector(sender, *data):
        """Callback de StateVector
        Entrée Ivy: (A écrire, des strings)
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        pass

    def on_dirto(sender, *data):
        """Callback de DIRTO
        Entrée Ivy: WptName: string
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        pass

    def on_time_start(sender, *data):
        """Callback de Time t=0.0
        Entrée Ivy: Rien
        Sortie Ivy: 3 messages sur Ivy
            - InitStateVector
            - WindComponent
            - MagneticDeclination
        """
        pass

    def on_limit_msg(sender, *data):
        """Retourne une liste de Waypoints (un PDV) depuis un fichier
        Entrée Ivy: (Message de limites)
        Sortie: Met à jour le phi max en mémoire
        """
        pass

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
