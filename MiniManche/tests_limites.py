#fonction pour tester avec les différentes configuration des volets
import limites2
from math import *
KT2MS=0.514444
DEG2RAD=0.017453
FT2M=0.3048
R=278.05
T0=288.16
gamma_constante=1.4
def test_configuration_physique(avion):
    #configuration numéro 1 : trains sortis
    if avion.train==True:
        if avion.config_physique==0:
            if avion.alt<10000*FT2M:
                if avion.Mach==False and avion.vitesse_lim == 250 * KT2MS and avion.vitesse_i == 220 * KT2MS and avion.nz_lim== [0,2.5] and avion.nx_lim==[-0.5, 0.5]:
                    return True
            else:
                if avion.Mach==False and avion.vitesse_lim==280*KT2MS and avion.vitesse_i==280*KT2MS and avion.nz_lim==[0,2.5] and avion.nx_lim==[-0.5,0.5]:
                    return True
        if avion.config_physique==1:
            if avion.Mach==False and avion.vitesse_lim==230*KT2MS and avion.vitesse_i==230*KT2MS and avion.nz_lim==[0,1.5] and avion.nx_lim==[-0.5,0.5]:
                return True
        if avion.config_physique==2:
            if avion.Mach==False and avion.vitesse_lim==200*KT2MS and avion.vitesse_i==200*KT2MS and avion.nz_lim==[0,1.5] and avion.nx_lim==[-0.5,0.5]:
                return True
        if avion.config_physique==3:
            if avion.Mach==False and avion.vitesse_lim==185*KT2MS and avion.vitesse_i==185*KT2MS and avion.nz_lim==[0,1.5] and avion.nx_lim==[-0.5,0.5]:
                return True
        if avion.config_physique==4:
            if avion.Mach==False and avion.vitesse_lim==177*KT2MS and avion.vitesse_i==177*KT2MS and avion.nz_lim==[0,1.5] and avion.nx_lim==[-0.5,0.5]:
                return True
    #configuration avec trains rentrés
    else:
        if avion.config_physique==1:
            if avion.Mach==False and avion.vitesse_lim==230*KT2MS and avion.vitesse_i==230*KT2MS and avion.nz_lim==[0,2] and avion.nx_lim==[-1,1]:
                return True
        if avion.config_physique == 2:
            if avion.Mach==False and avion.vitesse_lim == 200 * KT2MS and avion.vitesse_i == 200 * KT2MS and avion.nz_lim == [0,2] and avion.nx_lim==[-1, 1]:
                return True
        if avion.config_physique == 3:
            if avion.Mach==False and avion.vitesse_lim == 185 * KT2MS and avion.vitesse_i == 185 * KT2MS and avion.nz_lim == [0,2] and avion.nx_lim==[-1, 1]:
                return True
        if avion.config_physique == 4:
            if avion.Mach==False and avion.vitesse_lim == 177 * KT2MS and avion.vitesse_i == 177 * KT2MS and avion.nz_lim == [0,2] and avion.nx_lim==[-1, 1]:
                return True
        if avion.config_physique==0:
            if avion.alt<=10000*FT2M:
                if avion.Mach==False and avion.vitesse_lim == 250 * KT2MS and avion.vitesse_i == 220 * KT2MS and avion.nz_lim == [-1,2.5] and avion.nx_lim==[-1.5, 1.5]:
                    return True
            if 10000*FT2M<avion.alt<24600*FT2M:
                if avion.Mach==False and avion.vitesse_lim == 350 * KT2MS and avion.vitesse_i == 320 * KT2MS and avion.nz_lim == [-1,2.5] and avion.nx_lim==[-1.5, 1.5]:
                    return True

            if avion.alt>24600*FT2M:
                T = T0 - 6.5 * (avion.alt / 1000)
                a = sqrt(gamma_constante * R * T)
                if avion.Mach==True and avion.vitesse_lim == a*0.82 and avion.vitesse_i == a*0.78 and avion.nz_lim == [-1, 2.5] and avion.nx_lim==[-1.5,1.5]:
                    return True
    return False

def test_limites_angles(avion):
    if abs(avion.phi)>=30*DEG2RAD or abs(avion.gamma)>=25*DEG2RAD:
        if avion.PA==False and avion.phi_lim==[-67*DEG2RAD,67*DEG2RAD] and avion.gamma_lim==[-30*DEG2RAD,30*DEG2RAD]:
            return True
    else:
        if avion.PA==True and avion.phi_lim==[-33*DEG2RAD,33*DEG2RAD] and avion.gamma_lim==[-25*DEG2RAD,25*DEG2RAD]:
            return True
        if avion.PA==False and avion.phi_lim==[-67*DEG2RAD,67*DEG2RAD] and avion.gamma_lim==[-30*DEG2RAD,30*DEG2RAD]:
            return True
    return False

def test_limites_p(avion):
    if avion.PA==False:
        if avion.phi>=67*DEG2RAD and avion.p_lim==[-15*DEG2RAD,0]:
            return True
        if avion.phi<=-67 * DEG2RAD and avion.p_lim==[0,15 * DEG2RAD]:
            return  True
        if -67*DEG2RAD<avion.phi<67*DEG2RAD and avion.p_lim==[-15*DEG2RAD,15*DEG2RAD]:
            return  True
    if avion.PA==True:
        if avion.phi>=33*DEG2RAD and avion.p_lim==[-15*DEG2RAD,0]:
            return True
        if avion.phi<=-33 * DEG2RAD and avion.p_lim==[0,15 * DEG2RAD]:
            return  True
        if -33*DEG2RAD<avion.phi<33*DEG2RAD and avion.p_lim==[-15*DEG2RAD,15*DEG2RAD]:
            return  True
    return  False




def test():
    window=None
    #Créer votre avion ici en entrant les paramétres souhaités dans la liste ci dessous en respectant les contraintes suivantes
    #Les vitesses doivent être exprimées en m/s, les angles en radian
    #Mach est un booléen : True si la vitesse est calculée en fonction de la vitesse du son dans l'air, False sinon
    #PA = True : le PA est actif
    #train=True : les trains sont sortis
    #config_physique = désigne la configuration physique de l'avion, chiffre allant de 0 à 4
    #liste des paramètres dans l'ordre : altitude en mètre, vitesse, Mach,config_physique,train,phi,gamma,PA
    l=[25600* FT2M, 100 * KT2MS, False, 4, True, 29 * DEG2RAD, 55 * DEG2RAD, True]
    A320 = limites2.Avion(window)
    A320.alt = l[0]
    A320.vitesse = l[1]
    A320.Mach = l[2]
    A320.config_physique = l[3]
    A320.train = l[4]
    A320.phi = l[5]
    A320.gamma = l[6]
    A320.PA = l[7]
    A320.update_PA()
    A320.phi_limites()# ordre de ces deux fonctions importants
    A320.gamma_limites()
    A320.nx_limites()
    A320.nz_limites()
    A320.p_limites()
    A320.vitesse_indiquee()
    A320.vitesse_limite()
    print(test_configuration_physique(A320))
    print(test_limites_angles(A320))
    print(test_limites_p(A320))

test()