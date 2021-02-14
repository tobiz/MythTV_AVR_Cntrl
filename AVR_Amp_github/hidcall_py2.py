
import subprocess
import sys

#
# Trying to run python2 script from python3 environment
#

def main(relay, state):
	p_relay = "relay val=" + relay
	p_state = "state val=" + state
	
	print ("python3: p_relay=%s, P_state=%s\n" % (p_relay, p_state))
	
	#p = subprocess.run(["python2", "/home/pjr/hidtest10.py", "idVendor=0x16c0", "idProduct=0x05df", p_relay, p_state, "/dev/null"])
	p = subprocess.run(["python2", "/home/pjr/Development/AVR_Amp/hid_API.py", "idVendor=0x16c0", "idProduct=0x05df", p_relay, p_state, "/dev/null"])
	return

if __name__ == '__main__':
 
	relay = sys.argv[1]
	state = sys.argv[2]
	print ("python3: relay=%s, state=%s\n" % (relay,state))
	main(relay, state)
	
	exit()
	
	
	
	
	
	