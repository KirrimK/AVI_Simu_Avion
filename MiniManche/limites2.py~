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
	def __init__(self,alt,vitesse,Mach,config_physique,train,phi,gamma,PA,window,nx_lim,nz_lim,p_lim,vitesse_lim,vitesse_i,phi_lim,gamma_lim):#penser à virer tous les paramètres une fois tous les tests effectués et à tout mettre à 0 après
		self.alt=alt
		self.vitesse=vitesse#pas initialisé à 0
		self.Mach=Mach#booléen
		self.config_physique=config_physique #numéro de la configuration physique dans laquelle on se trouve (0,1,2,3
		self.train=train#booléen
		self.phi=phi
		self.gamma=gamma
		self.PA=PA#booléen
		self.window=window
		self.nz_lim=nz_lim
		self.nx_lim=nx_lim
		self.p_lim=p_lim
		self.vitesse_lim=vitesse_lim
		self.vitesse_i=vitesse_i
		self.phi_lim=phi_lim
		self.gamma_lim=gamma_lim


	def update_sliders(self,config_physique,train):
		pass
	def update_PA(self):
		self.PA=self.window.isAPOn
	def vitesse_limite(self):
	#dépend de l'altitude et de la configuration physique de l'avion
		limite_alt=[10000*FT2M,24600*FT2M]
		if self.train==False and self.config_physique==0:
			if self.alt<limite_alt[0]:
				self.Mach=False
				self.vitesse_lim=250*KT2MS
			if limite_alt[0]<self.alt<limite_alt[1]:
				self.Mach=False
				self.vitesse_lim=350*KT2MS
			if self.alt>limite_alt[1]:
				self.Mach=True
			#Mach maximal=0.82
			#calcul du Mach
				T=T0-6.5*(self.alt/1000)
				a=sqrt(gamma_constante*R*T)
				self.vitesse_lim=0.82*a
		if self.train==True and self.config_physique==0:
			self.Mach=False
			self.vitesse_lim=280*KT2MS

		if self.config_physique==1:
			self.Mach=False
			self.vitesse_lim=230*KT2MS
		if self.config_physique==2:
			self.Mach=False
			self.vitesse_lim=200*KT2MS
		if self.config_physique==3:
			self.Mach=False
			self.vitesse_lim=185*KT2MS
		if self.config_physique==4:
			self.Mach=False
			self.vitesse_lim=177*KT2MS

	def vitesse_indiquee(self):
		alt_lim=[10000*FT2M,24600*FT2M]
		self.vitesse_i=0
		if self.config_physique==0 and self.train==False:
			if self.alt<alt_lim[0]:
				self.vitesse_i=220*KT2MS
			if alt_lim[0]<self.alt<alt_lim[1]:
				self.vitesse_i=320*KT2MS
			if self.alt>alt_lim[1]:
				self.Mach=True
				#Mach consigne=0.78
				#calcul du Mach
				T=T0-6.5*(self.alt/1000)
				a=sqrt(gamma_constante*R*T)
				self.vitesse_i=0.78*a
		if self.train==True and self.config_physique==0:
			self.Mach=False
			self.vitesse_i=280*KT2MS

		if self.config_physique==1:
			self.Mach=False
			self.vitesse_i=230*KT2MS
		if self.config_physique==2:
			self.Mach=False
			self.vitesse_i=200*KT2MS
		if self.config_physique==3:
			self.Mach=False
			self.vitesse_i=185*KT2MS
		if self.config_physique==4:
			self.Mach=False
			self.vitesse_i=177*KT2MS
	def nz_limites(self):
		#les limitations du facteur de charge dépendent de la configuration physique de l'avion
		#tester si ces limites fonctionnent bien avec les trains sortis
		if self.train==False:
			if self.config_physique==0:
				self.nz_lim=[-1,2.5]
			else:
				self.nz_lim=[0,2]
		if self.train==True:
			if self.config_physique==0:
				self.nz_lim=[0,2.5]
			else:
				self.nz_lim=[0,1.5]

	def nx_limites(self):
		#il va falloir tester si ces limites ne sont pas trop restrictives, rien trouvé pour l'instant dans la doc et on a trouvé ça après discution avec M.Rouillard
		if self.train==False:
			if self.config_physique==0:
				self.nx_lim=[-1.5,1.5]
			else:
				self.nx_lim=[-1,1]
		else:
			self.nx_lim=[-0.5,0.5]

	def p_limites(self):
		if self.PA==False:
			if self.phi>=67*DEG2RAD:
				self.p_lim=[-15*DEG2RAD,0]
			if self.phi<=-67*DEG2RAD:
				self.p_lim=[0,15*DEG2RAD]
			else:
				self.p_lim=[-15*DEG2RAD,15*DEG2RAD] #pour l'exprimer en rad
		else:
			if self.phi>=33*DEG2RAD:
				self.p_lim=[-15*DEG2RAD,0]
			if self.phi<=-33*DEG2RAD:
				self.p_lim=[0,15*DEG2RAD]
			else:
				self.p_lim=[-15*DEG2RAD,15*DEG2RAD] #pour l'exprimer en radian/s
	def phi_limites(self):
		if abs(self.phi)>33*DEG2RAD:
			self.PA=False
			#self.window.onButtonPushSignal(True)#on force l'AP à ê off c'est pour ça que l'on a true et pas false
		if self.PA==False:
			self.phi_lim=[-67*DEG2RAD,67*DEG2RAD]
		else:
			self.phi_lim=[-33*DEG2RAD,33*DEG2RAD]

	def gamma_limites(self):
		if abs(self.gamma)>25*DEG2RAD:
			self.PA=False
			#self.window.onButtonPushSignal(True)
			self.phi_lim=[-67*DEG2RAD,67*DEG2RAD]
		if self.PA==False:
			self.gamma_lim=[-30*DEG2RAD,30*DEG2RAD]
		else:
			self.gamma_lim=[-25*DEG2RAD,25*DEG2RAD]

	def reception_vecteur_etat(self,alt,vitesse,gamma,phi):
		self.alt=alt #le z du state vector
		self.vitesse=vitesse
		self.gamma=gamma #le fpa du vecteur propre
		self.phi=phi
		self.update_PA()
		self.phi_limites()#ordre de ces deux fonctions importants
		self.gamma_limites()
		self.nx_limites()
		self.nz_limites()
		self.p_limites()
		self.vitesse_indiquee()
		self.vitesse_limite()


		
			
			

if __name__=='__main__':
	window=None
	for i in range(0,5):
		print(i)
		A320=Avion(25000*FT2M,100*KT2MS,False,i,False,29*DEG2RAD,55*DEG2RAD,True,window,0,0,0,0,0,0,0)
		print("alt=",A320.alt/FT2M)
		print("vitesse=",A320.vitesse/KT2MS)
		print("Config_physique=",A320.config_physique)
		print("train=",A320.train)
		print("vitesse_lim=",A320.vitesse_lim)
		A320.vitesse_limite()
		print("vitesse_lim update=",A320.vitesse_lim/KT2MS)
		print("Mach=",A320.Mach)
		T = T0 - 6.5 * (A320.alt / 1000)
		a = sqrt(gamma_constante * R * T)
		print(A320.vitesse_lim/a)
		print("phi=",A320.phi/DEG2RAD)
		print("gamma=",A320.gamma)
		print("nz_limites=",A320.nz_lim)
		A320.nz_limites()
		print("nz_limites update=",A320.nz_lim)
		print("nx_lim=",A320.nx_lim)
		A320.nx_limites()
		print("nx_lim update=",A320.nx_lim)
		print("p_lim=",A320.p_lim)
		A320.p_limites()
		print("p_lim_update=",A320.p_lim[0]/DEG2RAD,A320.p_lim[1]/DEG2RAD)
		print("vitesse_i=",A320.vitesse_i)
		A320.vitesse_indiquee()
		print("vitesse_i update=",A320.vitesse_i/KT2MS)
		print(A320.vitesse_i/a)
		print("phi-lim=",A320.phi_lim)
		A320.phi_limites()
		print("gamma_lim=",A320.gamma_lim)
		A320.gamma_limites()
		print("phi_lim update=",A320.phi_lim[0]/DEG2RAD,A320.phi_lim[1]/DEG2RAD)
		print("gamma_lim update=",A320.gamma_lim[0]/DEG2RAD,A320.gamma_lim[1]/DEG2RAD)
		print("PA=", A320.PA)

#à faire : repasser tout en méthodes de la classe avion et rajouter les limites en paramètres
		#faire la connexion avec les sliders de la fenêtre window
		#connexion avec le state vector pour alt,vitesse,gamma et phi
