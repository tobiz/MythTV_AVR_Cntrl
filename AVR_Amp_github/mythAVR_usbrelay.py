import hid



#PJR

#This relay object uses the HID library instead of usb. 
#Some scant details about the USB Relay
#http://vusb.wikidot.com/project:driver-less-usb-relays-hid-interface
#cython-hidapi module:
#https://github.com/trezor/cython-hidapi
#Installing the module:
#sudo apt-get install python-dev libusb-1.0-0-dev libudev-dev
#pip install --upgrade setuptools
#pip install hidapi
#A list of avaible methods for the hid object:
#https://github.com/trezor/cython-hidapi/blob/6057d41b5a2552a70ff7117a9d19fc21bf863867/chid.pxd#L9


#class Relay(object):
class Relay():
    #docstring for Relay
    def __init__(self, idVendor=0x16c0, idProduct=0x05df):
        
        self.h = hid.Device(idVendor, idProduct)
        
        
    def get_switch_statuses_from_report(self, report):
       
        # Grab the 8th number, which is a integer
        switch_statuses = report[7]

        # Convert the integer to a binary, and the binary to a list.
        switch_statuses = [int(x) for x in list('{0:08b}'.format(switch_statuses))]

        # Reverse the list, since the status reads from right to left
        switch_statuses.reverse()
        return switch_statuses

    def sendfeaturereport( self, message):
    	  print("send_feature_report, message is:", message)
    	  #self.h.send_feature_report(message, len(message))
    	  
    	  self.h.send_feature_report( {0x41, 0x01}) 
    	  #self.h.send_feature_report( [0x41, 0x01]) 
    	  #self.h.send_feature_report( b"\0x41\0x01") 

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
                    #message = [0xFF, relay]
                    message = [0xFF, int(relay)]
                else:
                    #message = [0xFD, relay]
                    message = [0xFD, int(relay)]

            self.sendfeaturereport(message)
            #send_feature_report(message)
            
           

#import hid
if __name__ == '__main__':
	vid = 0x16c0 
	pid = 0x05df
	#with hid.Device(vid, pid) as h:
		
		#print(f'Device manufacturer: {h.manufacturer}')
		
		#print(f'Product: {h.product}')
		#print(f'Serial Number: {h.serial}')
	relay = Relay(idVendor=0x16c0, idProduct=0x05df)
	print ("Relay 1 state is: ", relay.state(1))
	print ("Set Relay 1 state True")
	#relay.state(1, on=True)
	relay.state(1, on=False)
	print ("Relay 1 state is: ", relay.state(1))
	exit()
	"""
   sleep(2)

   # Turn all switches off
   print ("\nSet Relay 1 state False")
   relay.state(1, on=False)
   print ("Relay 1 state: ", relay.state(1))
   
   sleep(2)
    
   print ("\nSet Relay 1 state True")
   relay.state(1, on=True)
   print ("Relay 1 state: ", relay.state(1))
   sleep(2)
    
   print ("\nSet Relay 1 state False")
   relay.state(1, on=False)
   print ("Relay 1 state: ", relay.state(1))
   exit()

   # Print the state of all switches
   #print relay.state(0)
   """
    
