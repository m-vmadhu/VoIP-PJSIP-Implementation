
import sys
import pjsua as pj
import time
import socket
import threading
call = None
# Function for printing callback class Logs
def log_cb(level, str, len):
    print(str)

# Account Callback class to get notifications of Account registration
class SipAccountCallback(pj.AccountCallback):

    def __init__(self, acc):
        pj.AccountCallback.__init__(self, acc)

# Call Callback to receive events from Call
class SipCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    def on_state(self):
        print("Call is :", self.call.info().state_text),
        print("last code :", self.call.info().last_code),
        print("(" + self.call.info().last_reason + ")")
        if self.call.info().state_text == 'DISCONNCTD':
            global call
            call = None

    # This is the notification when call's media state is changed
    def on_media_state(self):

        global libObj
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            libObj.instance().conf_connect(call_slot, 0)
            libObj.instance().conf_connect(0, call_slot)
            
# Main Program
try:  
    # Starting of the Main Class
    # Step 1: First we need to Create library instance - which is the base class for the rest of the classes
    libObj = pj.Lib()  

    # Step 2: Instantiating the library with the default configuration
    libObj.init(log_cfg = pj.LogConfig(level=3, callback=log_cb))

    # Step 3: Configuring the Transport Object 
    transObj = pj.TransportConfig()

    print "************************REGISTRATION PROCESS BEGINS************************"
    # Step 4: Define the SIP Port
    transObj.port = 5060      
    
    # Step 5: Let the PJSIP know the client machine address 
    clientIP=raw_input("python SIPClient IP : ")
    print "Using default SIP Port: 5060\n\n"
    transObj.bound_addr = clientIP
    transport = libObj.create_transport(pj.TransportType.UDP,transObj)
    # Starting the Library class
    libObj.start()
    libObj.set_null_snd_dev()
    #Information to create header of REGISTER SIP message
    serverIP=raw_input("Proxy Server IP address:")
    uName=raw_input("\nUsername: ")
    secret=raw_input("\nPassword: ")
    #Set the userName as the display name
    dName=uName
    aConfig = pj.AccountConfig(domain = serverIP, username = uName, password = secret, display = dName)
    aConfig.id = "sip:"+uName
    aConfig.reg_uri = 'sip:'+serverIP+':5060'
    aCallBack = SipAccountCallback(aConfig)
    account = libObj.create_account(aConfig,cb=aCallBack)

    # creating instance of AccountCallback class
    account.set_callback(aCallBack)    
    print "\n******Registration Completed*******"
    print('\nRegistration Status=', account.info().reg_status, \
         '(' + account.info().reg_reason + ')')    
    # Main Loop for call handling
    while True:        
        #print "My SIP URI is", my_sip_uri
        print "Basic Facilities Available:\n y=make call \n h=hangup call \n q=quit\n"
        choice = sys.stdin.readline().rstrip("\r\n")
        if choice == "y" or choice =="Y":
            if call:
                print "Already have another call"
                continue
            print "\n\n URI Format: sip:username@userIP:userPort\n\n"
            destiURI=raw_input("Please enter the destination URI: ")
            if choice == "":
                continue
            lock = libObj.auto_lock()
            call = account.make_call(destiURI, SipCallCallback())         
            del lock           
        elif choice == "h" or choice =="H":
            if not call:
                print "There is no call"
                continue
            call.hangup()
            call = None
        elif choice == "q" or choice == "Q":
            break
    # Shutdown the library
    print"********** Unregistering *************"
    time.sleep(2)
    print "*********** Destroying Libraries *************"
    time.sleep(2)
    transport = None
    account.delete()
    account = None
    libObj.destroy()
    libObj = None
    sys.exit(0)


except pj.Error, e:

    print("Exception: " + str(e))
    libObj.destroy()
    libObj = None
    sys.exit(0)
