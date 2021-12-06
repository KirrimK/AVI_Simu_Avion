#import des modules utiles
from math import *

#Pour les valeurs des limites, on part des infos données par SimCockpit pour un Airbus A320

#vitesse désignera la vitesse propre de l'avion qui nous sera donnée par le State Vector -> en m/s
#altitude = hauteur exprimée en m = z donné par le State Vector 
#config_physique : peut prendre 5 valeurs : 0,10,20,30 et 40 pour les volets
#train : booléen true= train sorti
#Mach, quand Mach = True on calcule la vitesse limite en fonction de la vitesse du son dans l'air  
#au début on initialise : avion au décollage donc tout à 0 et train d'atterrissage sorti 


#gradient de température qui nous intéresse : -6,5K tous les km

#Pour le calcul de la vitesse de consigne= vitesse indiquée on définit arbitrairement la valeur du cost index = 0.50 pour un A320 volant avec Air France sur du vol moyen courier 

#Constante utile
KT2MS=0.514444
DEG2RAD=0.017453
FT2M=0.3048
gamma_constante=1.4
R=278.05 
T0=288.16 #en Kelvin
CI=0.35 #Cost Index


class Avion:
	def __init__(self,alt,vitesse_i,vitesse,Mach,nx,nz,p,config_physique,train,phi,gamma,PA):
		self.alt=0
		self.vitesse_i=0
		self.vitesse=0
		self.Mach=False
		self.nx=0
		self.nz=0
		self.p=0
		self.configuration_physique=1
		self.train=True 
		self.phi=0
		self.gamma=0
		self.PA=True 


def vitesse_limite(self.alt,self.vitesse_lim):
	#dépend de l'altitude et de la configuration physique de l'avion
	limite_alt=[10000*FT2M,24600*FT2M]
	vitesse_lim=0
	if self.train==False and self.config_physique==0:
		if self.alt<limite_alt[0]:
			self.Mach=False
			vitesse_lim=250*KT2MS
		if limite_alt[0]<self.alt<limite_alt[1]:
			self.Mach=False
			vitesse_lim=350*KTS2MS
		if self.alt>limite_alt[1]:
			self.Mach=True
			#Mach maximal=0.82
			#calcul du Mach
			T=T0-6.5*(self.alt/1000)
			a=sqrt(gamma_constante*R*T)
			vitesse_lim=0.82*a
	if self.train==True and self.config_physique==0:
		self.Mach=False
		vitesse_lim=280*KT2MS

	if self.config_physique==1:
		self.Mach=False
		vitesse_lim=230*KT2MS
	if self.config_physique==2:
		self.Mach=False
		vitesse_lim=200*KT2MS
	if self.config_physique==3:
		self.Mach=False
		vitesse_lim=185*KT2MS
	if self.config_physique==FULL:
		self.Mach=False
		vitesse_lim=177*KT2MS
		
	return self.Mach,vitesse_lim

def nz_limites(self.train,self.config_physique):
	#les limitations du facteur de charge dépendent de la configuration physique de l'avion
	#tester si ces limites fonctionnent bien avec les trains sortis
	nz_lim=[0,0] #liste avec les valeurs limites de nz
	if self.train==False:
		if self.config_physique==0:
		 	nz_lim=[-1,2.5]
		else:
			nz_lim=[0,2]
	if self.train=True:
		if self.config_physique==0:
			nz_lim=[0,2.5]
		else:
			nz_lim=[0,1.5]
	return nz_lim
	
def nx_limites(self.train,self.config_physique):
	#il va falloir tester si ces limites ne sont pas trop restrictives, rien trouvé pour l'instant dans la doc et on a trouvé ça après discution avec M.Rouillard
	nx_lim=[0,0]
	if self.train==False:
		if self.config_physique==0:
			nx_lim=[-1.5,1.5]
		else:
			nx_lim=[-1,1]
	else:
		nx_lim=[-0.5,0.5]
	return nx_lim
	
def p_lim():
	p_lim=15*DEG2RAD #pour l'exprimer en radian/s
	return p_lim
	
def phi_lim(self.PA):
	phi_lim=[0,0]
	if abs(self.phi)>33*DEG2RAD:
		self.PA=False 
	if self.PA==False:
		phi_lim=[-67*DEG2RAD,67*DEG2RAD]
	if self.PA==True:
		phi_lim=[-33*DEG2RAD,33*DEG2RAD]
	return phi_lim
	
#limite en gamma 25,30 


	
		
			
			
	

