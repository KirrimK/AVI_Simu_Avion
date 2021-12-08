#import des modules utiles
from math import *

#Pour les valeurs des limites, on part des infos données par SimCockpit pour un Airbus A320

#vitesse désignera la vitesse propre de l'avion qui nous sera donnée par le State Vector -> en m/s
#altitude = hauteur exprimée en m = z donné par le State Vector 
#config_physique : peut prendre 5 valeurs : 0,10,20,30 et 40 pour les volets
#train : booléen true= train sorti
#Mach, quand Mach = True on calcule la vitesse limite en fonction de la vitesse du son dans l'air  
#au début on initialise : avion au décollage et on prendra les valeurs du state vector initial  


#gradient de température qui nous intéresse : -6,5K tous les km

#Pour le calcul de la vitesse de consigne= vitesse indiquée on définit arbitrairement la valeur du cost index = 0.50 pour un A320 volant avec Air France sur du vol moyen courier -> à voir plus tard pour l'instant faire avec le modèle proposé par M.Rouillard = mettre une vitesse de commande dépendant de l'altitude 

#Constante utile
KT2MS=0.514444
DEG2RAD=0.017453
FT2M=0.3048
gamma_constante=1.4
R=278.05 
T0=288.16 #en Kelvin
CI=0.35 #Cost Index




class Avion:
	def __init__(self,alt,vitesse,Mach,config_physique,train,phi,gamma,PA,window):
		self.alt=alt
		self.vitesse=vitesse#pas initialisé à 0
		self.Mach=Mach#booléen
		self.configuration_physique=config_physique #numéro de la configuration physique dans laquelle on se trouve (0,1,2,3
		self.train=train#booléen
		self.phi=phi
		self.gamma=gamma
		self.PA=PA#booléen
                self.window=window
        def reception_vecteur_etat(self,alt,vitesse,gamma,phi):
                self.alt=alt #le z du state vector
                self.vitesse=vitesse
                self.gamma=gamma #le fpa du vecteur propre
                self.phi=phi


def vitesse_limite(avion):
	#dépend de l'altitude et de la configuration physique de l'avion
	limite_alt=[10000*FT2M,24600*FT2M]
	vitesse_lim=0
	if avion.train==False and avion.config_physique==0:
		if avion.alt<limite_alt[0]:
			avion.Mach=False
			vitesse_lim=250*KT2MS
		if limite_alt[0]<avion.alt<limite_alt[1]:
			avion.Mach=False
			vitesse_lim=350*KT2MS
		if avion.alt>limite_alt[1]:
			avion.Mach=True
			#Mach maximal=0.82
			#calcul du Mach
			T=T0-6.5*(avion.alt/1000)
			a=sqrt(gamma_constante*R*T)
			vitesse_lim=0.82*a
	if avion.train==True and avion.config_physique==0:
		avion.Mach=False
		vitesse_lim=280*KT2MS

	if avion.config_physique==1:
		avion.Mach=False
		vitesse_lim=230*KT2MS
	if avion.config_physique==2:
		avion.Mach=False
		vitesse_lim=200*KT2MS
	if avion.config_physique==3:
		avion.Mach=False
		vitesse_lim=185*KT2MS
	if avion.config_physique==4:
		avion.Mach=False
		vitesse_lim=177*KT2MS
		
	return avion.Mach,vitesse_lim

def vitesse_i(avion):
        alt_lim=[10000*FT2M,24600*FTSM]
        vitess_i=0
        if avion.config_physique==0 and avion.train=False:
                if avion.alt<alt_lim[0]:
                        vitesse_i=220*KTS2MS
                if alt_lim[0]<avion.alt<alt_lim[1]:
                        vitesse_i=320*KTS2MS
                if avion.alt>alt_lim[1]:
                        avion.Mach=True
                        #Mach consigne=0.78
			#calcul du Mach
			T=T0-6.5*(avion.alt/1000)
			a=sqrt(gamma_constante*R*T)
			vitesse_i=0.78*a
        if avion.train==True and avion.config_physique==0:
                avion.Mach=False
		vitesse_i=280*KT2MS

	if avion.config_physique==1:
		avion.Mach=False
		vitesse_i=230*KT2MS
	if avion.config_physique==2:
		avion.Mach=False
		vitesse_i=200*KT2MS
	if avion.config_physique==3:
		avion.Mach=False
		vitesse_i=185*KT2MS
	if avion.config_physique==4:
		avion.Mach=False
		vitesse_i=177*KT2MS
def nz_limites(avion):
	#les limitations du facteur de charge dépendent de la configuration physique de l'avion
	#tester si ces limites fonctionnent bien avec les trains sortis
	nz_lim=[0,0] #liste avec les valeurs limites de nz
	if avion.train==False:
		if avion.config_physique==0:
			nz_lim=[-1,2.5]
		else:
			nz_lim=[0,2]
	if avion.train==True:
		if avion.config_physique==0:
			nz_lim=[0,2.5]
		else:
			nz_lim=[0,1.5]
	return nz_lim
	
def nx_limites(avion):
	#il va falloir tester si ces limites ne sont pas trop restrictives, rien trouvé pour l'instant dans la doc et on a trouvé ça après discution avec M.Rouillard
	nx_lim=[0,0]
	if avion.train==False:
		if avion.config_physique==0:
			nx_lim=[-1.5,1.5]
		else:
			nx_lim=[-1,1]
	else:
		nx_lim=[-0.5,0.5]
	return nx_lim
	
def p_lim():
	p_lim=15*DEG2RAD #pour l'exprimer en radian/s
	return p_lim
	
def phi_lim(avion):
	phi_lim=[0,0]
	if abs(avion.phi)>33*DEG2RAD:
		avion.PA=False
                avion.window.onButtonPushSignal(True)
	if avion.PA==False:
		phi_lim=[-67*DEG2RAD,67*DEG2RAD]
	if avion.PA==True:
		phi_lim=[-33*DEG2RAD,33*DEG2RAD]
	return phi_lim
	
#limite en gamma 25,30

def limite_gamma(avion):
        gamma_lim=[0,0]
        if abs(avion.gamma)>25*DEG2RAD:
                avion.PA=False
                avion.window.onButtonPushSignal(True)
        if avion.PA==False:
                gamma_lim=[-30*DEG2RAD,30*DEG2RAD]
        else:
                gamma_lim=[-25*DEG2RAD,25*DEG2RAD]
        return gamma_lim
	
		
			
			

if __name__=='__main__':
        A320=Avion(6000,113,)
        
        
