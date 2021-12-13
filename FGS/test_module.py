from ivy.std_api import *
from fgs_module import *
import time

msgr = "None"

def on_msg(agent, *data):
	global msgr
	msgr = data[0]
	print(msgr)

def test_msg(msge,f):
	global msgr
	IvySendMsg(msge)
	print(msge)
	f.write(msge + '\n')
	time.sleep(1.0)
	f.write(msgr + '\n' + '\n')

def test_pdv_nominal():
	f = open('test_pdv_nominal.txt','w')
	
	reset_fgs("pdv_test.txt")
	#test nominal
	test_msg("StateVector x=10000 y=0 z=5000 Vp=128 fpa=0 psi=1.57 phi=0", f)
	#test flyBy
	test_msg("StateVector x=27000 y=0 z=5000 Vp=128 fpa=0 psi=1.57 phi=0", f)
	#test overFly
	test_msg("StateVector x=30000 y=29999 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	#test overFly
	test_msg("StateVector x=30000 y=30001 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	#test DirtoRequest
	test_msg("StateVector x=0 y=0 z=5000 Vp=128 fpa=0 psi=3.14 phi=0", f)
	
	f.close()

def test_pdv_selecte():
	f = open('test_pdv_selecte.txt','w')
	
	reset_fgs("pdv_test.txt")
	#test flyBy
	test_msg("StateVector x=60000 y=-10000 z=5000 Vp=128 fpa=0 psi=1.57 phi=0", f)
	#test overFly before
	test_msg("StateVector x=40000 y=20000 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	#test overFly after sans passage
	test_msg("StateVector x=40000 y=40000 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	
	reset_fgs("pdv_test.txt")
	#test overFly after avec passage
	test_msg("StateVector x=31000 y=31000 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	test_msg("StateVector x=31000 y=40000 z=7000 Vp=128 fpa=0 psi=0 phi=0", f)
	
	f.close()

def test_time_init():
	f = open('test_time_init.txt','w')
	
	reset_fgs("pdv_test.txt")
	test_msg("Time t=1.0",f)
	
	f.close()
	
def reset_fgs(pdv):
	IvySendMsg("RESETFGS {}".format(pdv))
	time.sleep(1.0)

if __name__=="__main__":
	IvyInit("FGS_test", "Ready")
	IvyStart("127.0.0.1:2010") #IP à changer
	time.sleep(3.0)
	IvyBindMsg(on_msg, "(.*)")
	test_pdv_nominal()
    
