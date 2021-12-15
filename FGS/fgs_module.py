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

RESET_REGEX = "RESETFGS (\S+)" #uniquement à des fins de tests unitaires

TARGET_MSG = "Target X={} Y={} Z={} Khi={}"

FLYBY = "flyBy"
OVERFLY = "overFly"

KTS2MS = 0.5144447
DEG2RAD = 0.01745329

NM2M = 1852
GRAV = 9.81

DEBUG = True #True printera sur la stdout
ALLOW_RESET = False #True permettra de reset le FGS au pt de départ pdt l'exécution

def print_debug(text):
    if DEBUG:
        print(text)

InitStateVector=[0, 0, 0, 214*KTS2MS, 0, 0, 0] #la vitesse de décollage est de 110 m/s

def resetFGS(sender, *data):
    if ALLOW_RESET:
        print_debug("--------FGS HAS BEEN RESET--------")
        global fgs
        fgs.unbind()
        fgs = FGS(data[0],0,0,0.2389)
    else:
        IvySendMsg("Resetting has not been allowed.")

class Waypoint:
    """
    Objet contenant les informations d'un Waypoint
    """
    def __init__(self, name, x, y, z, mode):
        self.nom = name #string
        self.x = float(x) #float
        self.y = float(y) #float
        self.z = float(z) #float
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
            if ligne not in ["", "WPTNAME X Y Z MODE"]:
                list = ligne.split()
                listWpt.append(Waypoint(list[0],list[1],list[2],list[3],list[4]))
    return listWpt 

def trianglevitesses(vwind, dirwind, vp, psi):
    #calculer vecteur vsol
    vsvec = [vp*math.cos(psi)+vwind*math.cos(math.pi*dirwind), vp*math.sin(psi)+vwind*math.sin(math.pi*dirwind)]
    #vsol = math.sqrt(vsvec[0]**2+vsvec[1]**2)
    route = math.atan2(vsvec[1], vsvec[0])
    return route

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
        self.phi_max = 27*DEG2RAD #radians (valeur par défaut pour éviter div/zero)
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
        print_debug("--------ON_STATE_VECTOR--------")
        print_debug(data)
        print_debug("\n")
        def basculer_waiting_dirto(x, y, lastsent): #lastsent comme lastsenttarget
            #nope, dirtorequest
            print_debug("BASCULER_DIRTO:")
            self.waiting_dirto = True #devient VRAI car on envoie une dirto request
            #derive = math.asin(self.vwind*math.sin(route_actuelle-self.dirwind)/self.state_vector[3]*math.cos(fpa)) # calculer
            #route_actuelle = psi + derive
            route_actuelle = trianglevitesses(self.vwind, self.dirwind, self.state_vector[3], self.state_vector[5])
            IvySendMsg("DirtoRequest")
            self.lastsenttarget = (x, y, lastsent[2], route_actuelle) #on met à jour la dernière target envoyée
            print_debug(self.lastsenttarget)
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target

        def passer_wpt_suiv(axe_next):
            new_tgt = self.flight_plan[self.current_target_on_plan] #on définit une nouvelle target à partir du plan de vol (elle devient notre target actuelle)
            _, x_wpt, y_wpt, z_wpt, tgtmode = new_tgt.infos() #on prend les infos de la target (infos dont on a besoin)
            contrainte = z_wpt # la contrainte correspond à l'altitude
            if contrainte < 0:
                found_next = False #on initialise à FAUX le fait qu'on n'ait pas encore trouvé la prochaine contrainte
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
        x, y, z, vp, fpa, psi, phi = data
        self.state_vector = [float(x), float(y), float(z), float(vp), float(fpa), float(psi), float(phi)]
        x, y, z, vp, fpa, psi, phi = self.state_vector
        
        if not self.waiting_dirto:
            #calculer le reculement du seuil en fonction du waypoint qui suit
            wpt_target = self.flight_plan[self.current_target_on_plan].infos() #on prend les infos de la target actuelle
            print_debug("WPT_target:")
            print_debug(wpt_target)
            distance_max = 1*NM2M #on définit la distance maximale d'écart entre l'avion et la route
            
            if self.dirto_on:
                axe_actuel = self.lastsenttarget[3]
            elif self.current_target_on_plan != 0: #si la target actuelle n'est pas le premier wpt
                print_debug("PASPREMIER")
                wpt_target_before = self.flight_plan[self.current_target_on_plan-1].infos() #on regarde le wpt précédent la target actuelle
                print_debug("WPT_before:")
                print_debug(wpt_target_before)
                axe_actuel = math.atan2(wpt_target[1]- wpt_target_before[1], wpt_target[2]- wpt_target_before[2]) #on calcule la route actuelle
            else: #si c'est le premier wpt
                print_debug("PREMIER")
                axe_actuel = trianglevitesses(self.vwind, self.dirwind, vp, psi) #on calcule la route actuelle en utilisant les données du initstatevector
            
            
            if self.current_target_on_plan != len(self.flight_plan)-1: #si la target actuelle n'est pas le dernier wpt
                print_debug("PASDERNIER")
                wpt_target_next = self.flight_plan[self.current_target_on_plan+1].infos() #on prend les données de la prochaine target
                print_debug("WPT_next:")
                print_debug(wpt_target_next)
                axe_next = math.atan2(wpt_target_next[1]- wpt_target[1], wpt_target_next[2]- wpt_target[2]) #la route correspond à la route actuelle
            else: #si la target est le dernier wpt
                print_debug("DERNIER")
                axe_next = axe_actuel #de même la prochain target correspond à la target actuelle
            
            if self.targetmode == OVERFLY: 
                print_debug("seuil_ex: 0(overfly)")
                seuil_ex = 0 #on initialise le seuil ex à O
            else: #si c'est le mode FlyBy
                delta_khi = abs(axe_next - axe_actuel) #on calcule la variation de route
                if delta_khi >= math.pi * 0.5: #saturation en cas de demi tours
                    delta_khi = math.pi * 0.5
                seuil_ex = vp**2/(GRAV*math.tan(self.phi_max))*math.tan(delta_khi/2) #on calcule le seuil ex
                print_debug("seuil_ex: {}".format(seuil_ex))

            print_debug("axe_actuel: {}".format(axe_actuel))
            print_debug("axe_next: {}".format(axe_next))

            ex = math.sin(axe_actuel)*(x-wpt_target[1])+math.cos(axe_actuel)*(y-wpt_target[2])
            distance = math.sqrt((x-wpt_target[1])**2+(y-wpt_target[2])**2)#on calcule la distance de l'avion par rapport à la target
            print_debug("ex {} distance {}".format(ex, distance))
        else:
            print("Waiting DIRTO")

        #si en mode dirto
        if self.dirto_on: #si dirto demandé
            print_debug("DIRTO_ON")
            #dirto flyby par défaut
            if (ex >= seuil_ex):
                print_debug("D_PASSE")
                self.dirto_on = False
                #Envoyer la prochaine target
                self.current_target_on_plan += 1
                if self.current_target_on_plan >= len(self.flight_plan): #si l'indice de la target actuelle est supérieur à la longueur du pdv
                    print_debug("D_BASCULEWAIT")
                    basculer_waiting_dirto(x, y, self.lastsenttarget) #on a fini le pdv et on applique la route de la dernière target
                else: #sinon
                    print_debug("D_NEXT")
                    passer_wpt_suiv(axe_next) #on passe au wpt suivant
            else: #si ex < -seuil_ex
                print_debug("D_PASENCORE")
                IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target
        elif self.waiting_dirto: #si on attend une dirto
            print_debug("WAITING")
            #en attente de dirto, maintenir l'avion sur axe lorsque dépassé point sans séquencer
            IvySendMsg(TARGET_MSG.format(*self.lastsenttarget))
        #Sinon
        else: #si dirto pas demandé et si pas attente de dirto
            print_debug("NORMAL")
            if self.targetmode == OVERFLY:
                print_debug("N_OVERFLY")
                if (ex > -seuil_ex):
                    print_debug("NO_PASSE")
                    #vérifier si distance inf à distmax
                    if (distance < distance_max): #si la distance de l'avion par rapport à la route est < à la distance_max
                        print_debug("NO_PROCHE")
                        #ok, séquencer et, passer au suivant
                        self.current_target_on_plan += 1 #on regarde la target suivante
                        if self.current_target_on_plan >= len(self.flight_plan): #si l'indice de la target actuelle est supérieur à la longueur du pdv
                            print_debug("NO_DERNIER_BASCULERWAITING")
                            basculer_waiting_dirto(x, y, self.lastsenttarget) #on a fini le pdv et on applique la route de la dernière target
                        else: #sinon
                            print_debug("NO_NEXT")
                            passer_wpt_suiv(axe_next) #on continue le pdv en passant au wpt suivant
                    else: #si la distance de l'avion par rapport à la route est > à la distance maximale
                        print_debug("NO_LOUPE")
                        basculer_waiting_dirto(x, y, self.lastsenttarget) #on a fini le pdv et on applique la route de la dernière target
                else: #si ex < -seuil_ex
                    print_debug("NO_PASENCORE")
                    #pas encore dépassé le point
                    IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target
            else: #si le mode est FlyBy
                print_debug("FLYBY")
                if (ex >= -seuil_ex):
                    print_debug("NF_PASSE")
                    #ok, séquencer et, passer au suivant
                    self.current_target_on_plan += 1 #on regarde la target suivante
                    if self.current_target_on_plan >= len(self.flight_plan):
                        print_debug("NF_DERNIER_BASCULER")
                        basculer_waiting_dirto(x, y, self.lastsenttarget)
                    else:
                        print_debug("NF_PASDERNIER_NEXT")
                        passer_wpt_suiv(axe_next)
                else:
                    #pas encore
                    print_debug("NF_PASENCORE")
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
        print("--------ON_DIRTO--------")
        (dirto_wpt,) = data
        print("Requested waypoint {}".format(dirto_wpt))
        if self.waiting_dirto: #si dirto demandé
            self.waiting_dirto = False #on modifie le waiting_dirto à FALSE car on n'est plus en attente d'un dirto
        #chercher le wpt dans la liste des wpt non séquencés, via recherche linéaire
        for i in range(self.current_target_on_plan%len(self.flight_plan), len(self.flight_plan)):
            if self.flight_plan[i].name() == dirto_wpt:
                #get les infos du Wpt
                _, x_wpt, y_wpt, z_wpt, _ = self.flight_plan[i].infos() #on prend les infos de la target actuelle
                #calculer la direction à mettre
                route = math.atan2(y_wpt-self.state_vector[1], x_wpt-self.state_vector[0]) #on calcule la route 
                #trouver la prochaine contrainte d'altitude, s'il n'y en a pas, garder la plus récente
                contrainte = z_wpt
                if contrainte == -1:
                    found_next = False #on initialise à FAUX le fait qu'on n'ait pas encore trouvé la prochaine contrainte
                    for j in range(i, len(self.flight_plan)): #pour chaque wpt dans le pdv
                        if self.flight_plan[j].infos()[3] != -1: #si l'altitude z du wpt j est égale à -1
                            contrainte = self.flight_plan[j].infos()[3] #on met à jour la contrainte avec cette valeur -1
                            break
                    if not found_next: #si on a la prochaine contrainte
                        contrainte = self.lastsenttarget[2] #on met à jour la contrainte avec celle de la dernière target
                #sauvegarder le message à envoyer
                self.lastsenttarget = (x_wpt, y_wpt, contrainte, route) #on met à jour la dernière target
                self.targetmode = FLYBY #on met le mode de la target en FlyBY
                self.current_target_on_plan = i #on met à jour le numéro de la target en cours
                self.dirto_on = True #on active le mode dirto
                print("DIRTO TO {}".format(self.lastsenttarget))
                IvySendMsg(TARGET_MSG.format(*self.lastsenttarget)) #on envoie la dernière target
                break
        

    def on_time_start(self, sender, *data):
        """Callback de Time t=1.0
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
    if ALLOW_RESET:
        if DEBUG:
            print("Mode test")
        else:
            print("Mode test silencieux")
    else:
        if DEBUG:
            print("Débugging activé en mode production")
        else:
            print("Mode production")

    IvyInit("FGS", "Ready")
    IvyStart("127.255.255.255:2010") #IP à changer
    time.sleep(1.0)
    IvyBindMsg(resetFGS, RESET_REGEX)
    fgs = FGS("fpl_formaté.txt", 0, 0, 0.2389)
    IvyMainLoop()

##### Pour référence future #####
#IvySendMsg("")
#IvyBindMsg(callback, "regex")

#def generic_callback(sender, *data):
#    pass


#with FGS("", fdve, efd, rftr) as fgs_test1:
#    dujghb fpathconf
#    tests