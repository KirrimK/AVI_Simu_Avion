# FGS_module

from ivy.std_api import *
import time
IvyInit("FGS", "Ready")
IvyStart("10.1.127.255:2010") #IP à changer
time.sleep(1.0)

#IvySendMsg("")
#IvyBindMsg(callback, "regex")

#def generic_callback(sender, *data):
#    pass

class Waypoint:
    """
    Objet contenant les informations d'un Waypoint
    """
    def __init__(self, name, x, y, z, mode):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode

    def infos(self):
        return (self.name, self.x, self.y, self.z, self.mode)

class FGS:
    """
    L'objet contenant toutes les fonctions et variables du FGS
    """

    def __init__(self, filename):
        """Constructeur du FGS
        Entrée: filename: string
        """
        pass
        self.load_flight_plan(filename)

    def on_state_vector(sender, *data):
        """Callback de StateVector
        Entrée Ivy: (A écrire, des strings)
        Sortie Ivy: Aucun message ou 1 message
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

    def load_flight_plan(filename):
        """Retourne une liste de Waypoints (un PDV) depuis un fichier
        Arguments: filename: string
        Retourne: flight_plan: Waypoint list
        """
        pass
