import matplotlib.pyplot as plt
from ivy.std_api import *
from math import pi
import time

### PLACER LE FICHIER MATLAB DANS LE MEME REPERTOIRE QUE CE FICHIER PYTHON
### Renommer le fichier txt en "ResultSimuMatlab" ou modifier le nom ci-dessous

#Lecture du fichier
fic = open("CaptureCap90.txt","r")
lignes = fic.readlines()
fic.close()

T, cap, fpa, phi, V, Vi, Vs, X, Y, ey, H, nx, nz, p = [], [], [], [], [], [], [], [], [], [], [], [], [], []

for donnees in lignes[1:] :
    infos = donnees.split(",")
    
    T.append(float(infos[0]))       # temps en secondes
    cap.append(float(infos[1]))     # cap en rad
    fpa.append(float(infos[2]))     # fpa en rad
    phi.append(float(infos[3]))     # phi en rad
    V.append(float(infos[4]))       # vitesse en m/s
    Vi.append(float(infos[5]))      # vitesse indiquée en m/s
    Vs.append(float(infos[6]))      # vitesse verticale en ft/min
    X.append(float(infos[7]))       # position x en m
    Y.append(float(infos[8]))       # position y en m
    ey.append(float(infos[9]))      # cross-track error en m
    H.append(float(infos[10]))      # altitude en m
    nx.append(float(infos[11]))     # facteur de charge sur x sans unités
    nz.append(float(infos[12]))     # facteur de charge sur z sans unités
    p.append(float(infos[13]))      # vitesse de roulis en rad/s

#Si l'on souhaite afficher directement la courbe de matlab  
plt.figure()
plt.plot(T, p)
#plt.show()

#Courbe à envoyer pour comparer directement sur le même graphique
courbe_matlab=p
#Creation du state_vector à envoyer
state_vector = [ [X[k], Y[k], H[k], V[k], fpa[k], cap[k], phi[k], courbe_matlab[k]]for k in range(len(T))]

#Fonctions pour l'application Ivy
def on_cx_proc(agent,connected):
    pass
def on_die_proc(agent,_id):
    pass

#Initialisation de la communication
app_name="MyIvyApplication"
ivy_bus = "127.255.255.255:2021"
IvyInit(app_name,"Ready",0,on_cx_proc,on_die_proc)
IvyStart(ivy_bus)

#Paramètres à modifier en fonction du fichier et des données à envoyer
Vwind = 40 * 1852/3600 
dirWind =  0 *pi/180
Khi = 90 * pi/180
val_lateral = 90 #Cap/route en mode selected
dm = 0 *pi/180 #Déclinaison magnétique
time.sleep(1.0)

#Messages envoyés pour tester l'application
IvySendMsg("WindComponent VWind="+str(Vwind)+" dirWind="+str(dirWind))
IvySendMsg("MagneticDeclination mag="+str(dm))
IvySendMsg("FCULateral Mode=SelectedHeading Val="+str(val_lateral))
IvySendMsg("FCUVertical Altitude=7000 Mode=Selected Val=0")
#IvySendMsg("FCUSpeedMach Mode=SelectedSpeed Val=200")
IvySendMsg("MM VC=200")
IvySendMsg("MM Limites vMin=40 vMax=400 phiLim=35 nxMin=-2.5 nxMax=2.5 nzMin=-2.5 nzMax=2.5 pLim=0.5")
for i in state_vector :
    st_x, st_y, st_z, st_vp, st_fpa, st_psi, st_phi = str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6])
    IvySendMsg("StateVector x="+st_x+" y="+st_y+" z="+st_z+" Vp="+st_vp+" fpa="+st_fpa+" psi="+st_psi+" phi="+st_phi)
    IvySendMsg("Courbe valeur="+str(i[7]))
    IvySendMsg("Target X=1000 Y=1000 Z=2133 Khi="+str(Khi))
IvySendMsg("Trace Bool=1")
IvyStop()