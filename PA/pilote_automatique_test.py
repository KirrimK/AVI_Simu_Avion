from ivy.std_api import *
import time
import matplotlib.pyplot as plt
from math import asin, cos, sin, pi, sqrt

class IvyPA():
    def __init__(self):
        self.vwind = 0
        self.dirwind = 0
        self.dm = 0
        self.cap = 0
        self.cap_consigne= 0
        self.route_consigne=0
        self.route = 0
        self.lateral_mode = "Managed"
        self.vertical_mode = "Managed"
        self.speed_mode = "Managed"
        self.speed = 0
        self.mach = 0
        self.vitesse_c = 0
        self.mach_c = 0
        self.pente_c = 0
        self.target_X= 0
        self.target_Y = 0
        self.target_Z = 0
        self.target_khi = 0
        self.altitude_c = 0
        self.vitesse =0
        self.vertical_val = 0
        self.state_vector = [0,0,1524,0,0,0,0,0]
        self.Nx = 0
        self.Nz=0
        self.P=0
        self.vmin = 0
        self.vamx = 0
        self.phiLim = 0
        self.nxMin = 0
        self.nxMax = 0
        self.nzMin = 0
        self.nzMax = 0
        self.pLim = 0
        #Listes stockant les valeurs pour tracer les courbes
        self.xs = []
        self.ys = []
        self.zs = []
        self.temps=[0]
        self.ps=[0]
        self.phics=[]
        self.routes=[]
        self.fpas=[]
        self.nzs=[]
        self.nxs=[]
        self.Courbe=[0]

    def on_cx_proc(agent,connected):
        pass

    def on_die_proc(agent,_id):
        pass

    def on_msg_wind(self,agent,*data):

        self.vwind = float(data[0])
        self.dirwind = float(data[1])

    def on_msg_dm(self,agent,*data):
        self.dm = float(data[0])

    def on_msg_state_vector(self,agent,*data):
        print("message reçu")
        self.state_vector = [float(x) for x in list(data)]
        self.xs.append(self.state_vector[0])
        self.ys.append(self.state_vector[1])
        self.zs.append(self.state_vector[2])
        self.vitesse=self.state_vector[3]
        self.fpas.append(self.state_vector[4])
        self.cap=self.state_vector[5]
        self.phi=self.state_vector[6] 

    def on_msg_FCULateral(self,agent,*data):
        self.lateral_mode = data[0]
        if self.lateral_mode=="SelectedTrack":
            self.route_consigne=float(data[1]) * pi/180
        elif self.lateral_mode=="SelectedHeading":
            self.cap_consigne=float(data[1]) * pi/180

    def on_msg_speed_mm(self,agent,*data):

        if self.speed_mode!="SelectedSpeed" and self.speed_mode!="SelectedMach":
            self.speed_mode="Mini_Manche"
            self.vitesse_c=float(data[0])
            self.vitesseic_to_vitessec()

    def on_msg_SpeedMach(self,agent,*data):

        self.speed_mode = data[0]
        if self.speed_mode=="SelectedSpeed":
            self.vitesse_c=float(data[1])*1852/3600 #Vitesse de consigne reçue en kts
            self.vitesseic_to_vitessec()
        elif self.speed_mode=="SelectedMach":
            self.mach_c=float(data[1])
        
    def on_msg_FCUVertical(self,agent,*data):

        #Altitude de consigne reçue en ft
        self.altitude_c=float(data[0])*0.3048
        self.vertical_mode = data[1]
        self.vertical_val = float(data[2])

    def on_msg_limites(self,agent,*data):
        self.vmin=float(data[0])
        self.vmax=float(data[1])
        self.phiLim=float(data[2])
        self.nxMin=float(data[3])
        self.nxMax=float(data[4])
        self.nzMin=float(data[5])
        self.nzMax=float(data[6])
        self.pLim=float(data[7])

    def on_msg_target(self,agent,*data):
        self.target_X=float(data[0])
        self.target_Y=float(data[1])
        self.target_Z=float(data[2])
        self.target_khi=float(data[3])

        self.temps.append(self.temps[-1]+1) #On créé la liste des temps
        #Calcul de nx, nz et p à envoyer
        self.calcul_lateral()
        self.calcul_vertical()
        self.calcul_vitesse()
        #Envoi de nx, nz et p
        self.send_msg()

    def calcul_lateral(self):
        if self.lateral_mode == "SelectedHeading" :
            self.p()
            #Ajout à la liste si l'on veut afficher la courbe
            self.ps.append(self.P)

        elif self.lateral_mode == "SelectedTrack" : 
            self.routec_to_capc() #On se ramène à une catpure de cap
            self.p()
            self.ps.append(self.P)

        else :
            ey = -sin(self.target_khi)*(self.state_vector[0] - self.target_X) + cos(self.target_khi)*(self.state_vector[1] - self.target_Y)
            x_dot = self.state_vector[3]*cos(self.state_vector[5])*cos(self.state_vector[4]) + self.vwind*cos(pi+self.dirwind)
            y_dot = self.state_vector[3]*sin(self.state_vector[5])*cos(self.state_vector[4]) + self.vwind*sin(pi+self.dirwind)
            GS = sqrt(x_dot**2 + y_dot**2)
            ey_dot=-ey/(tau_ey*GS)
            #On limite pour respecter le domaine de asin
            if ey_dot<-1:
                ey_dot=-1
            elif ey_dot>1:
                ey_dot=1

            self.route_consigne = self.target_khi + asin(ey_dot) #On se ramène à une capture de route

            self.routec_to_capc() #On se ramène à une catpure de cap
            self.p()
            self.ps.append(self.P)

    def calcul_vertical(self):

        if self.vertical_mode == "Selected":
            a=((self.altitude_c - self.state_vector[2])/tau_h)/self.state_vector[3]
            #On limite pour respecter le domaine de asin
            if a>1:
                a=1
            elif a<-1:
                a=-1
            self.pente_c = asin(a)
            self.nz()
            #Ajout à la liste si l'on veut afficher la courbe
            self.nzs.append(self.Nz)
            
        elif self.vertical_mode == "Managed" :
            b=((self.target_Z - self.state_vector[2])/tau_h)/self.state_vector[3]
            if b>1:
                b=1
            elif b<-1:
                b=-1
            self.pente_c = asin(b)
            self.nz()
            self.nzs.append(self.Nz)

    def calcul_vitesse(self):
        if self.speed_mode == "SelectedSpeed":
            self.nx()
            #Ajout à la liste si l'on veut afficher la courbe
            self.nxs.append(self.Nx)
        elif self.speed_mode == "SelectedMach":
            self.machc_to_vitessec() #Conversion Mach de consigne en vitesse de consigne
            self.nx()
            self.nxs.append(self.Nx)
        elif self.speed_mode == "Mini_Manche":
            self.nx()
            self.nxs.append(self.Nx)

    def on_msg_courbe(self,agent,*data):
        self.Courbe.append(float(data[0]))

    def send_msg(self):
        IvySendMsg("AutoPilot nx="+str(self.Nx)+" nz ="+str(self.Nz)+" rollRate="+str(self.P))
    
    def p(self) :

        angle=self.cap_consigne - self.cap +self.dm
        #Boucles permettant à l'avion de ne pas tourner de plus de 180°
        while angle>=pi:
            angle-=2*pi
        while angle<-pi:
            angle+=2*pi

        phic=(Ve/g) * ((angle)/tau_psi)
        #Saturation en angle de tangage, 33°
        if phic<-33*pi/180: 
            phic=-33*pi/180
        elif phic>33*pi/180:
            phic=33*pi/180
        
        #Ajout à la liste si l'on veut afficher la courbe
        self.phics.append(phic)
        self.P=(1/tau_phi) * ( phic - self.phi)
        #Application des limitations
        self.P=self.limite(-self.pLim,self.pLim,self.P)

    def vitesseic_to_vitessec(self):
        self.vitesse_c = self.vitesse_c + self.state_vector[2]*1852/(3600*2*100*0.3048)
        #Application des limitations
        self.vitesse_c=self.limite(self.vmin,self.vmax,self.vitesse_c)

    def machc_to_vitessec(self):
        self.vitesse_c = self.mach_c *600 * 1852/3600 

    def routec_to_capc(self) :
        self.cap_consigne=self.route_consigne - asin( (self.vwind * sin(self.route_consigne + self.dm  - self.dirwind))/(self.state_vector[3]*cos(self.state_vector[4])))

    def nx(self) :
        self.Nx=(self.vitesse_c - self.state_vector[3])/(tau_v*g) + sin(self.state_vector[4])
        #Applications des limitations
        self.Nx=self.limite(self.nxMin,self.nxMax,self.Nx)

    def nz(self) :
        self.Nz=((Ve/g)*((self.pente_c - self.state_vector[4])/tau_gamma)+cos(self.state_vector[4]))/cos(self.state_vector[6])
        #Application des limitations
        self.Nz=self.limite(self.nzMin,self.nzMax,self.Nz)

    def limite(self,xmin,xmax,x):
        #Fonction servant à limiter un paramètre
        if x > xmax:
            x=xmax
        elif x < xmin:
            x=xmin
        return x

    def on_msg_trace(self,agent,*data):

        self.trace(self.temps,self.ps,self.Courbe) #Trace les courbes, deuxième paramètre à modifier en fonction de ce que l'on veut, faire attention à ce que la courbe envoyée de matlab est la bonne

    def trace(self,temps,valeur_python,valeur_matlab):
        plt.plot(temps,valeur_python,"b",label="Courbe python")
        plt.plot(temps,valeur_matlab,"r--",label="Courbe matlab")
        plt.title("Capture de Cap 90°") #A modifier en fonction du fichier utilisé
        plt.xlabel("Temps (s)")
        plt.ylabel("p (rad/s)") #A modifier en fonction du paramètre à afficher
        plt.legend()
        plt.show()


if __name__=="__main__":
    
    #Paramètres servant aux différents calculs
    tau_phi, tau_ey = 3, 20
    tau_psi =  (1.4)**2*tau_phi
    tau_h = 32
    g = 9.81
    Ve = 180 * 1852/3600
    tau_v, tau_gamma = 1/(g*0.01), Ve/g 

    #Initialisation de la communication
    app_name="MyIvyApplication"
    ivy_bus = "127.255.255.255:2021"
    Ivypa=IvyPA()
    IvyInit(app_name,"Ready",0,IvyPA.on_cx_proc,IvyPA.on_die_proc)
    IvyStart(ivy_bus)

    #Abonnement aux différents messages
    IvyBindMsg(Ivypa.on_msg_wind,'^WindComponent VWind=(\S+) dirWind=(\S+)')
    IvyBindMsg(Ivypa.on_msg_dm,'^MagneticDeclination mag=(\S+)')
    IvyBindMsg(Ivypa.on_msg_FCULateral,'^FCULateral Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_SpeedMach,'^FCUSpeedMach Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_speed_mm,"^MM VC=(\S+)")
    IvyBindMsg(Ivypa.on_msg_state_vector,'^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)')
    IvyBindMsg(Ivypa.on_msg_FCUVertical,'^FCUVertical Altitude=(\S+) Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_target,"^Target X=(\S+) Y=(\S+) Z=(\S+) Khi=(\S+)")
    IvyBindMsg(Ivypa.on_msg_limites,"^MM Limites vMin=(\S+) vMax=(\S+) phiLim=(\S+) nxMin=(\S+) nxMax=(\S+) nzMin=(\S+) nzMax=(\S+) pLim=(\S+)")
    IvyBindMsg(Ivypa.on_msg_trace,"^Trace Bool=(\S+)") #Permet de tracer une fois tout le statevector reçu
    IvyBindMsg(Ivypa.on_msg_courbe,'^Courbe valeur=(\S+)') #Message pour recevoir la courbe matlab
    IvyMainLoop()