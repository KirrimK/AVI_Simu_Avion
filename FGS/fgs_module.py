# FGS_module

from ivy.std_api import *
import time
import math

STATEVEC_REGEX = "StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)"
WINDCOMP_REGEX = "WindComponent VWind={} dirWind={}"
DM_REGEX = "MagneticDeclination MagneticDeclination={}"
DIRTO_REGEX = "DIRTO Wpt=(\S+)"
TIMESTART_REGEX = "Time t=1.0"
LIMITES_REGEX = "MM Limites vMin=(\S+) vMax=(\S+) phiLim=(\S+) nxMin=(\S+) nxMax=(\S+) nzMin=(\S+) nzMax=(\S+) pLim=(\S+)"

TARGET_MSG = "Target X={} Y={} Z={} Khi={}"

FLYBY = "flyBy"
OVERFLY = "overFly"

KTS2MS = 0.5144447
DEG2RAD = 0.01745329

NM2M = 1852
GRAV = 9.81

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
        self.waiting_dirto = False
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
        self.idbind1 = IvyBindMsg(self.on_state_vector, STATEVEC_REGEX)
        self.idbind2 = IvyBindMsg(self.on_dirto, DIRTO_REGEX)
        self.idbind3 = IvyBindMsg(self.on_time_start, TIMESTART_REGEX)
        self.idbind4 = IvyBindMsg(self.on_limit_msg, LIMITES_REGEX)
    
    def __enter__(self):
        return self

    def unbind(self):
        IvyUnBindMsg(self.idbind1)
        IvyUnBindMsg(self.idbind2)
        IvyUnBindMsg(self.idbind3)
        IvyUnBindMsg(self.idbind4)
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.unbind()

    def on_state_vector(self, sender, *data):
        """Callback de StateVector
        Entrée Ivy:
            - x, y, z, vp, fpa, psi, phi: floats
        Sortie Ivy: 1 message sur Ivy
            - Target
        """
        def basculer_waiting_dirto(x, y, lastsent, psi):
            #nope, dirtorequest
            self.waiting_dirto = True
            derive = 0 # calculer
            route_actuelle = psi + derive
            IvySendMsg("DirtoRequest")
            self.lastsenttarget = (x, y, lastsent[2], route_actuelle)
            IvySendMsg(TARGET_MSG.format(*lastsent))
        
        def passer_wpt_suiv():
            new_tgt = self.flight_plan[self.current_target_on_plan]
            _, x_wpt, y_wpt, z_wpt, tgtmode = new_tgt.infos()
            contrainte = z_wpt
            if contrainte == -1:
                found_next = False
                for j in range(self.current_target_on_plan, len(self.flight_plan)):
                    if self.flight_plan[j].infos()[3] != -1:
                        found_next = True
                        contrainte = self.flight_plan[j].infos()[3]
                        break
                if not found_next:
                    contrainte = self.lastsenttarget[2]
            self.targetmode = tgtmode
            self.lastsenttarget = (x_wpt, y_wpt, contrainte, axe_next)
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))

        #mettre à jour les infos connues sur l'avion (unpack data)
        self.state_vector = [x, y, z, vp, fpa, psi, phi] = data
        #calculer le reculement du seuil en fonction du waypoint qui suit
        wpt_target = self.flight_plan[self.current_target_on_plan].infos()
        distance_max = 1*NM2M
        if self.targetmode == OVERFLY:
            seuil_ex = 0
        else:
            if self.current_target_on_plan != 0:
                wpt_target_before = self.flight_plan[self.current_target_on_plan-1].infos()
                axe_actuel = math.atan2(wpt_target[2]- wpt_target_before[2], wpt_target[1]- wpt_target_before[1])
            else:
                axe_actuel = math.atan2(wpt_target[2]-self.state_vector[1], wpt_target[1]-self.state_vector[0])
            
            if self.current_target_on_plan != len(self.flight_plan)-1:
                wpt_target_next = self.flight_plan[self.current_target_on_plan+1].infos()
                axe_next = axe_actuel = math.atan2(wpt_target_next[2]- wpt_target[2], wpt_target_next[1]- wpt_target[1])
            else:
                axe_next = axe_actuel
            delta_khi = axe_next - axe_actuel
            seuil_ex = vp**2/(GRAV*math.tan(self.phi_max))*math.tan(delta_khi/2)

        ex = math.cos(x-wpt_target[1])+math.sin(y-wpt_target[2])
        distance = math.sqrt((x-wpt_target[1])**2+(y-wpt_target[2])**2)

        #si en mode dirto
        if self.dirto_on:
            #dirto flyby par défaut
            if (ex > -seuil_ex):
                self.dirto_on
                #Envoyer la prochaine target
                self.current_target_on_plan += 1
                if self.current_target_on_plan >= len(self.flight_plan):
                    basculer_waiting_dirto(x, y, self.lastsenttarget, psi)
                else:
                    passer_wpt_suiv()
            else:
                IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
        elif self.waiting_dirto:
            #en attente de dirto, maintenir l'avion sur axe lorsque dépassé point sans séquencer
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
        #Sinon
        else:
            if self.targetmode == OVERFLY:
                if (ex > -seuil_ex):
                    #vérifier si distance inf à distmax
                    if (self.targetmode == OVERFLY and distance < distance_max):
                        #ok, séquencer et, passer au suivant
                        self.current_target_on_plan += 1
                        if self.current_target_on_plan >= len(self.flight_plan):
                            basculer_waiting_dirto(x, y, self.lastsenttarget, psi)
                        else:
                            passer_wpt_suiv()
                    else:
                        basculer_waiting_dirto(x, y, self.lastsenttarget, psi)
                else:
                    #pas encore
                    IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
            else:
                if (ex + seuil_ex > 0):
                    #ok, séquencer et, passer au suivant
                    self.current_target_on_plan += 1
                    if self.current_target_on_plan >= len(self.flight_plan):
                        basculer_waiting_dirto(x, y, self.lastsenttarget, psi)
                    else:
                        passer_wpt_suiv()
                else:
                    #pas encore
                    IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))

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
        if self.waiting_dirto:
            self.waiting_dirto = False
        #chercher le WPT dans la liste des WPTs non séquencés, via recherche linéaire
        for i in range(self.current_target_on_plan%len(self.flight_plan), len(self.flight_plan)):
            if self.flight_plan[i].name() == dirto_wpt:
                #get les infos du Wpt
                _, x_wpt, y_wpt, z_wpt, _ = self.flight_plan[i].infos()
                #calculer la direction à mettre
                route = math.atan2(y_wpt-self.state_vector[1], x_wpt-self.state_vector[0])
                #trouver la prochaine contrainte d'altitude, si il n'y en a pas, garder la plus récente
                contrainte = z_wpt
                if contrainte == -1:
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


#with FGS("", fdve, efd, rftr) as fgs_test1:
#    dujghb fpathconf
#    tests
