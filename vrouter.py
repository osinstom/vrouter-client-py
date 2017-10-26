from sleekxmpp import ClientXMPP, XMLStream, Iq
import time
import xml.etree.ElementTree
import logging
import argparse, sys, os

from xmppclient import XmppClient

logger = logging.getLogger(__name__)

vrouter = None

# Virtual Execution Environment (VEE)
class Vee():

    def __init__(self, identifier, network):
        self.identifier = identifier
        self.network = network
        self.attached = False
        self.operations = ['ping']

    def attach(self):
        vrouter.xmpp_agent.initial_subscribe(self.network)
        self.attached = True

    def detach(self):
        vrouter.xmpp_agent.unsubscribe(self.network)
        self.attached = False

    def info(self):
        print "ID={}, ATTACHED={}, NETWORK={}".format(self.identifier, self.attached, self.network)

    def console(self):
        os.system('clear')
        while True:
            print ("""
                ### {} VEE Command Line Interface ###
                ### List of operations: {} ###
                ### Type '0' to exit console. ###
            """).format(self.identifier, self.operations)
            action = raw_input("""Choose operation to invoke.\n""")
            if action == '0':
                break
            elif action == 'ping':
                self.ping()

    def ping(self):
        print "Pinging ... "

class VRouterMock():

    def __init__(self, client_jid):
        self.xmpp_agent = XmppClient(client_jid=client_jid, server_jid='bgp.contrail.com', password='passwd')
        self.xmpp_agent.connect(('127.0.0.1', 5269), use_tls=False, reattempt=False)
        self.xmpp_agent.process(block=False)

        self.vee_list = []

    def xmpp_session_started(self):
        return self.xmpp_agent.session_started

    def create_vee(self):
        identifier = raw_input("Type identifier of new VEE..\n")
        network = raw_input("Type a network the VEE should be attached to..\n")

        logger.info("Creating new Virtual Execution Environment..")
        vee = Vee(identifier, network)
        vee.attach()
        self.vee_list.append(vee)

    def list_vee(self):
        logger.info("Currently associated VEEs:\n")
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            vee.info()

    def enter_vee(self):
        identifier = raw_input("Type identifier of VEE..\n")
        vee = self.get_vee(identifier)
        if vee:
            vee.console()
        else:
            logger.warn("No VEE with specified identifier!")

    def delete_vee(self, identifier):
        vee = self.get_vee(identifier)
        vee.detach()
        self.vee_list.remove(vee)

    def detach_all_vee(self):
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            vee.detach()


    def get_vee(self, identifier):
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            if vee.identifier == identifier:
                return vee

    def shutdown(self):
        logger.info("Shutting vRouter down..")
        self.detach_all_vee()
        self.xmpp_agent.disconnect()


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    if not len(sys.argv) > 1:
        logger.error("Too few arguments")
    jid = sys.argv[1]
    vrouter = VRouterMock(jid)

    while not vrouter.xmpp_session_started():
        time.sleep(1)

    os.system('clear')

    while True:
        print ("""
            Console of vRouter {}..
            
            1.Create a new VEE
            2.List already connected VEE
            3.Enter VEE console
            4.Delete VEE
            5.Shutdown vRouter
            6.Exit/Quit console
            """)
        option = raw_input("Choose action from list above..\n")

        if option == "1":
            vrouter.create_vee()
        elif option == "2":
            vrouter.list_vee()
        elif option == "3":
            vrouter.enter_vee()
        elif option == "4":
            vrouter.delete_vee()
        elif option == "5":
            vrouter.shutdown()
            break












