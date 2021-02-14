
import hid
import sys


"""
PJR

This relay object uses the HID library instead of usb. 
Some scant details about the USB Relay
http://vusb.wikidot.com/project:driver-less-usb-relays-hid-interface
cython-hidapi module:
https://github.com/trezor/cython-hidapi
Installing the module:
sudo apt-get install python-dev libusb-1.0-0-dev libudev-dev
pip install --upgrade setuptools
pip install hidapi
A list of avaible methods for the hid object:
https://github.com/trezor/cython-hidapi/blob/6057d41b5a2552a70ff7117a9d19fc21bf863867/chid.pxd#L9

This only runs under Python2.7.  Won't run under Python3.x
"""

class Relay(object):
    """docstring for Relay"""
    
    def __init__(self, idVendor, idProduct, relay=1, state=False):
        self.h = hid.device()
        self.h.open(idVendor, idProduct)
        self.h.set_nonblocking(1)
        #print ("Python2 Relay Init")

    def get_switch_statuses_from_report(self, report):
        """
        The report returned is a 8 int list, ex:
        
        [76, 72, 67, 88, 73, 0, 0, 2]
        The ints are passed as chars, and this page can help interpret:
        https://www.branah.com/ascii-converter
        The first 5 in the list are a unique ID, in case there is more than one switch.
        The last three seem to be reserved for the status of the relays. The status should
        be interpreted in binary and in reverse order.  For example:
        2 = 00000010
        This means that switch 1 is off and switch 2 is on, and all others are off.
        """

        # Grab the 8th number, which is a integer
        switch_statuses = report[7]

        # Convert the integer to a binary, and the binary to a list.
        switch_statuses = [int(x) for x in list('{0:08b}'.format(switch_statuses))]

        # Reverse the list, since the status reads from right to left
        switch_statuses.reverse()

        # The switch_statuses now looks something like this:
        # [1, 1, 0, 0, 0, 0, 0, 0]
        # Switch 1 and 2 (index 0 and 1 respectively) are on, the rest are off.
        #print "switch statuses: ", switch_statuses
        
        print("Switch statuses: ", switch_statuses)
        return switch_statuses

    def send_feature_report(self, message):
    	  #print("send_feature_report: ", message)
    	  self.h.send_feature_report(message)

    def get_feature_report(self):
        # If 0 is passed as the feature, then 0 is prepended to the report. However,
        # if 1 is passed, the number is not added and only 8 chars are returned.
        feature = 1
        # This is the length of the report. 
        length = 8
        return self.h.get_feature_report(feature, length)

    def state(self, relay, on=None):
        """
        Getter/Setter for the relay.  
        Getter - If only a relay is specified (with an int), then that relay's status 
        is returned.  If relay = 0, a list of all the statuses is returned.
        True = on, False = off.
        Setter - If a relay and on are specified, then the relay(s) status will be set.
        Either specify the specific relay, 1-8, or 0 to change the state of all relays.
        on=True will turn the relay on, on=False will turn them off.
        """

        # Getter
        if on == None:
            if relay == 0:
                report = self.get_feature_report()
                switch_statuses = self.get_switch_statuses_from_report(report)
                status = []
                for s in switch_statuses:
                    status.append(bool(s))
            else:
                report = self.get_feature_report()
                switch_statuses = self.get_switch_statuses_from_report(report)
                status = bool(switch_statuses[relay-1])

            return status

        # Setter
        else:
            if relay == 0:
                if on:
                    message = [0xFE]
                else:
                    message = [0xFC]
            else:
                # An integer can be passed instead of the a byte, but it's better to
                # use ints when possible since the docs use them, but it's not neccessary.
                # https://github.com/jaketeater/simpleusbrelay/blob/master/simpleusbrelay/__init__.py
                if on:
                    message = [0xFF, relay]
                else:
                    message = [0xFD, relay]

            self.send_feature_report(message)
            
            
def main(idVendor, idProduct, relay_nos, state):
    	
    	#print ('Number of arguments:', len(sys.argv), 'arguments.')
    	#print ('Argument List:', str(sys.argv))
    
    	#idVendor = sys.argv[1]
    	#idProduct = sys.argv[2]
    
    	#kwargs = sys.kwargs
    
    	#print("idVendor=", idVendor)

    	# Create a relay object
    	relay = Relay(idVendor=0x16c0, idProduct=0x05df)
    	
    	print("Set Relay %i state %i" % (relay_nos, state))
    	relay.state(relay_nos, state)
    	print("Relay %i is now %i\n" % (relay_nos, relay.state(relay_nos)))
    	sleep(1)
    	return

    	# (Setter) Turn switch 1 on
    	#r1 = relay.state(1)
    	#print "Relay initial state: ", r1
    	#if r1 == True:
    	#    relay.state(1, on=False)
    	#    r2 = relay.state(1)
    	#    print "Current state was True, set: ", r2
    	#else:
    	#    relay.state(1, on=True)
    	#    r2 = relay.state(1)
    	#    print "Current state was False, set: ", r2
    	#exit()
    	#print "\n\n"
    	#sleep(2)
    
    	print ("Set Relay 1 state True")
    	relay.state(1, on=True)
    	print ("Relay 1 state is: ", relay.state(1))

    	sleep(2)

    	# Turn all switches off
    	print ("\nSet Relay 1 state False")
    	relay.state(1, on=False)
    	print ("Relay 1 state is: ", relay.state(1))
    
    	sleep(2)
    
    	print ("\nSet Relay 1 state True")
    	relay.state(1, on=True)
    	print ("Relay 1 state is: ", relay.state(1))
    	sleep(2)
    
    	print ("\nSet Relay 1 state False")
    	relay.state(1, on=False)
    	print ("Relay 1 state is: ", relay.state(1))
    	#exit()

    	# Print the state of all switches
    	#print relay.state(0)

if __name__ == '__main__':
    from time import sleep
    #print ('Number of arguments:', len(sys.argv), 'arguments.')
    #print ('Argument List:', str(sys.argv))
    idVendor = sys.argv[1].split("=")[1]
    idProduct = sys.argv[2].split("=")[1]
    relay = sys.argv[3].split("=")[1]
    state = sys.argv[4].split("=")[1]
    
    
    if state == "on":
    	state = 1
    else:
    	state = 0
    #print "idVendor= %s, idProduct=%s, relay=%s, state=%s" % (idVendor, idProduct, relay, state)
    main(idVendor, \
    	idProduct, \
    	int(relay), \
    	int(state))
    exit()
    