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

def resetFGS(sender,  data):
    print("FGS reset\n")
    global fgs
    fgs.unbind()
    fgs = FGS(data[0],0,0,0.2389)

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

def trianglevitesses(vwind, dirwind, vp, psi):
    #calculer vecteur vsol
    vsvec = [vp*math.cos(psi)+vwind*math.cos(math.pi*dirwind), vp*math.sin(psi)+vwind*math.sin(math.pi*dirwind)]
    vsol = math.sqrt(vsvec[0]**2+vsvec[1]**2)
    route = math.atan2(vsvec[1], vsvec[0])
    return vsol, route

class FGS:
    """
    L'objet contenant toutes les fonctions et variables du FGS
    """

    def __init__(self, filename, vwind, dirwind, MagneticDeclination):
        """Constructeur du FGS
        Arguments:
            - filename: string
        """
        self.dirto_on = False #flag qui indique si on est en mode dirto ou non
        self.waiting_dirto = False #flag qui indique si on est en attente d'un dirto
        self.dirto_target_number = 0 #numéro du WPT dans le PDV en target du dirto
        self.phi_max = 0 #radians
        self.flight_plan = load_flight_plan(filename) #list of Waypoint
        self.current_target_on_plan = 0 #numéro du WPT dans le PDV actuellement en target
        self.lastsenttarget = (0, 0, 0, 0) #x, y, contrainte, route
        self.targetmode = FLYBY
        self.vwind = vwind #m/s
        self.dirwind = dirwind #radians
        self.dm = MagneticDeclination #radians
        self.state_vector = InitStateVector.copy() #x, y, z, vp, fpa, psi, phi
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
        Sortie Ivy: 1/2 message sur Ivy
            - Target
            et optionnellement:
            - DirtoRequest
        """
        def basculer_waiting_dirto(x, y, lastsent): #lastsent comme lastsenttarget
            #nope, dirtorequest
            self.waiting_dirto = True #devient VRAI car on envoie une dirto request
            #derive = math.asin(self.vwind*math.sin(route_actuelle-self.dirwind)/self.state_vector[3]*math.cos(fpa)) # calculer
            #route_actuelle = psi + derive
            route_actuelle = trianglevitesses(self.vwind, self.dirwind, self.state_vector[3], self.state_vector[5])
            IvySendMsg("DirtoRequest")
            self.lastsenttarget = (x, y, lastsent[2], route_actuelle) #on met à jour la dernière target envoyée
            IvySendMsg(TARGET_MSG.format(*lastsent)) #on envoie la dernière target

        def passer_wpt_suiv(): #passer au wpt suivant
            new_tgt = self.flight_plan[self.current_target_on_plan] #on définit une nouvelle target à partir du plan de vol (elle devient notre target actuelle)
            _, x_wpt, y_wpt, z_wpt, tgtmode = new_tgt.infos() #on prend les infos de la target (infos dont on a besoin)
            contrainte = z_wpt # la contrainte correspond à l'altitude
            if contrainte == -1: 
                found_next = False #on initialise à FAUX le fait qu'on a pas encore trouvé la prochaine contrainte
                for j in range(self.current_target_on_plan, len(self.flight_plan)): #pour chaque target dans le plan de vol
                    if self.flight_plan[j].infos()[3] != -1: #si la contrainte de la target est -1
                        found_next = True #on connaît maintenant la prochaine contrainte
                        contrainte = self.flight_plan[j].infos()[3]
                        break
                if not found_next: #si on connaît déjà la prochaine contrainte
                    contrainte = self.lastsenttarget[2] #contrainte vaut l'altitude z de la dernière target
            self.targetmode = tgtmode #on applique aussi le mode de la target
            self.lastsenttarget = (x_wpt, y_wpt, contrainte, axe_next) #on met à jour la dernière target envoyée
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target

        #mettre à jour les infos connues sur l'avion (unpack data)
        self.state_vector = [x, y, z, vp, fpa, psi, phi] = data
        #calculer le reculement du seuil en fonction du waypoint qui suit
        wpt_target = self.flight_plan[self.current_target_on_plan].infos() #on prend les infos de la target actuelle
        distance_max = 1*NM2M #on définit la distance maximale d'écart entre l'avion et la route
        if self.targetmode == OVERFLY: 
            seuil_ex = 0 #on initialise le seuil ex à O
        else: #si c'est le mode FlyBy
            if self.current_target_on_plan != 0: #si la target actuelle n'est pas le premier wpt
                wpt_target_before = self.flight_plan[self.current_target_on_plan-1].infos() #on regarde le wpt précédent la target actuelle
                axe_actuel = math.atan2(wpt_target[2]- wpt_target_before[2], wpt_target[1]- wpt_target_before[1]) #on calcule la route actuelle
            else: #si c'est le premier wpt
                axe_actuel = math.atan2(wpt_target[2]-self.state_vector[1], wpt_target[1]-self.state_vector[0]) #on calcule la route actuelle en utilisant les données du initstatevector
            
            if self.current_target_on_plan != len(self.flight_plan)-1: #si la target actuelle n'est pas le dernier wpt
                wpt_target_next = self.flight_plan[self.current_target_on_plan+1].infos() #on prend les données de la prochaine target (on lit le pdv dans le sens inverse)
                axe_next = axe_actuel = math.atan2(wpt_target_next[2]- wpt_target[2], wpt_target_next[1]- wpt_target[1]) #la route correspond à la route actuelle
            else: #si la target est le dernier wpt
                axe_next = axe_actuel #de même la route de la prochaine target correspond à celle de la target actuelle
            delta_khi = axe_next - axe_actuel #on calcule la variation de route entre actuelle et suivante
            seuil_ex = vp**2/(GRAV*math.tan(self.phi_max))*math.tan(delta_khi/2) #on calcule le seuil ex

        ex = math.cos(x-wpt_target[1])+math.sin(y-wpt_target[2]) #à définir
        distance = math.sqrt((x-wpt_target[1])**2+(y-wpt_target[2])**2) #distance de l'avion par rapport à la target actuelle

        #si en mode dirto
        if self.dirto_on: #si dirto
            #dirto flyby par défaut
            if (ex > -seuil_ex):
                self.dirto_on
                #Envoyer la prochaine target
                self.current_target_on_plan += 1 #on passe à la prochaine target
                if self.current_target_on_plan >= len(self.flight_plan): #si l'indice de la target actuelle est supérieur à la longueur du pdv
                    basculer_waiting_dirto(x, y, self.lastsenttarget) #on a fini le pdv et on applique la route de la dernière target
                else: #si l'indice de la target est inférieur à la longueur du pdv
                    passer_wpt_suiv() #on passe au wpt suivante
            else: #si ex < -seuil_ex
                IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target
        elif self.waiting_dirto:
            #en attente de dirto, maintenir l'avion sur axe lorsque dépassé point sans séquencer
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
        #Sinon
        else: #si pas d'attente de dirto
            if self.targetmode == OVERFLY:
                if (ex > -seuil_ex):
                    #vérifier si distance inf à distmax
                    if (distance < distance_max):
                        #ok, séquencer et, passer au suivant
                        self.current_target_on_plan += 1 #on passe à la target suivante
                        if self.current_target_on_plan >= len(self.flight_plan): #si l'indice de la target actuelle est supérieur à la longueur du pdv
                            basculer_waiting_dirto(x, y, self.lastsenttarget) #on a fini le pdv et on applique la route de la dernière target
                        else: #sinon
                            passer_wpt_suiv() #on passe au wpt suivant
                    else:#si la distance est supérieur à la distance maximale
                        basculer_waiting_dirto(x, y, self.lastsenttarget) #on applique la route de la dernière target
                else:
                    #pas encore dépassé le point
                    IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
            else: #si le mode est FlyBy
                if (ex + seuil_ex > 0):
                    #ok, séquencer et, passer au suivant
                    self.current_target_on_plan += 1
                    if self.current_target_on_plan >= len(self.flight_plan):
                        basculer_waiting_dirto(x, y, self.lastsenttarget)
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
    IvyStart("127.0.0.1:2010") #IP à changer
    time.sleep(1.0)
    IvyBindMsg(resetFGS, "RESETFGS (\S+)")
    fgs = FGS("pdv.txt", 0, 0, 0.2389)
    IvyMainLoop()

##### Pour référence future #####
#IvySendMsg("")
#IvyBindMsg(callback, "regex")

#def generic_callback(sender, *data):
#    pass


#with FGS("", fdve, efd, rftr) as fgs_test1:
#    dujghb fpathconf
#    tests