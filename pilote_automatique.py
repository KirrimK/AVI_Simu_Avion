from ivy.std_api import *
import time

class IvyPA():
    def __init__(self,vwind=0,dirwind=0,dm=0,cap=0,route=0,lateral_mode="Managed",vertical_mode="Managed",speed_mode="Managed",speed=0,mach=0,altitude=0,vertical_val=0,state_vector=[],target_X=0,target_Y=0,target_Z=0,target_khi=0,vmin=0,vmax=0,phiLim=0,nxMin=0,nxMax=0,nzMin=0,nzMax=0,pLim=0):
        self.vwind = vwind
        self.dirwind = dirwind
        self.dm = dm
        self.cap = cap
        self.route = route
        self.lateral_mode = lateral_mode
        self.vertical_mode = vertical_mode
        self.speed_mode = speed_mode
        self.speed = speed
        self.mach = mach
        self.target_X= target_X
        self.target_Y = target_Y
        self.target_Z = target_Z
        self.target_khi = target_khi
        self.altitude = altitude
        self.vertical_val = vertical_val
        self.state_vector = state_vector
        self.vmin = vmin
        self.vamx = vmax
        self.phiLim = phiLim
        self.nxMin = nxMin
        self.nxMax = nxMax
        self.nzMin = nzMin
        self.nzMax = nzMax
        self.pLim = pLim
    def on_cx_proc(agent,connected):
        pass

    def on_die_proc(agent,_id):
        pass

    def on_msg_wind(self,agent,*data):

        self.vwind = int(data[0])
        self.dirwind = int(data[1])
        print("vwind=",self.vwind," dirwind=",self.dirwind)

    def on_msg_dm(self,agent,*data):
        self.dm = int(data[0])
        print("mag_dec = ",self.dm)

    def on_msg_state_vector(self,agent,*data):
        self.state_vector = [int(x) for x in list(data)]
        print("StateVector=",self.state_vector)

    def on_msg_FCULateral(self,agent,*data):
        self.lateral_mode = data[0]
        if self.lateral_mode=="SelectedTrack":
            self.route=int(data[1])
            print("Route=",self.route)
        elif self.lateral_mode=="SelectedHeading":
            self.cap=int(data[1])
            print("Cap=",self.cap)
        else:
            self.cap=0 #A modifier
            self.route=0

    def on_msg_SpeedMach(self,agent,*data):
        self.speed_mode = data[0]
        if self.speed_mode=="SelectedSpeed":
            self.speed=int(data[1])
            print("Speed=",self.speed)
        elif self.speed_mode=="SelectedMach":
            self.mach=int(data[1])
            print("Mach=",self.mach)
        
    def on_msg_FCUVertical(self,agent,*data):
        self.altitude=int(data[0])
        self.vertical_mode = data[1]
        self.vertical_val = int(data[2])
        print("Vertical_Mode=",self.vertical_mode)
        print("Altitude=",self.altitude)
        print("Vertical_val",self.vertical_val)
    def on_msg_target(self,agent,*data):
        self.target_X=int(data[0])
        self.target_Y=int(data[1])
        self.target_Z=int(data[2])
        self.target_khi=int(data[3])
        print("Target (X,Y,Z,Khi)=",(self.target_X,self.target_Y,self.target_Z,self.target_khi))
    def on_msg_limites(self,agent,*data):
        self.vmin=int(data[0])
        self.vmax=int(data[1])
        self.phiLim=int(data[2])
        self.nxMin=int(data[3])
        self.nxMax=int(data[4])
        self.nzMin=int(data[5])
        self.nzMax=int(data[6])
        self.pLim=int(data[7])
        print("Limites (vmin,vmax,phiLim,nxMin,nxMax,nzMin,nzMax,pLim)=",(self.vmin,self.vmax,self.phiLim,self.nxMin,self.nxMax,self.nzMin,self.nzMax,self.pLim))

if __name__=="__main__":

    app_name="MyIvyApplication"
    ivy_bus = "127.255.255.255:2021"
    Ivypa=IvyPA()
    IvyInit(app_name,"Ready",0,IvyPA.on_cx_proc,IvyPA.on_die_proc)
    IvyStart(ivy_bus)

    IvyBindMsg(Ivypa.on_msg_wind,'^WindComponent VWind=(\S+) dirWind=(\S+)')
    IvyBindMsg(Ivypa.on_msg_dm,'^MagneticDeclination=(\S+)')
    IvyBindMsg(Ivypa.on_msg_state_vector,'^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)')
    IvyBindMsg(Ivypa.on_msg_FCULateral,'^FCULateral Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_SpeedMach,'^SpeedMach Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_FCUVertical,'^FCUVertical Altitude=(\S+) Mode=(\S+) Val=(\S+)')
    IvyBindMsg(Ivypa.on_msg_target,"^Target X=(\S+) Y=(\S+) Z=(\S+) Khi=(\S+)")
    IvyBindMsg(Ivypa.on_msg_limites,"^MM Limites Vmin=(\S+) Vmax=(\S+) phiLim=(\S+) nxMin=(\S+) nxMax=(\S+) nzMin=(\S+) nzMax=(\S+) pLim=(\S+)")
    IvyMainLoop()