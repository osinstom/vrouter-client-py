from sleekxmpp import ClientXMPP, XMLStream, Iq
import time
import logging
import argparse, sys, os
import ConfigParser

from ovs import OVS
from util import PubInfo
from xmppclient import XmppClient


logger = logging.getLogger(__name__)

vrouter = None


# Virtual Execution Environment (VEE)
class Vee():

    def __init__(self, identifier, network, ip_addr):
        self.identifier = identifier
        self.network = network
        self.ip_address = ip_addr
        self.attached = False
        self.operations = ['ping']

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

    def __init__(self, client_jid, ip_address, controller_ip):
        self.xmpp_agent = XmppClient(client_jid=client_jid, server_jid='bgp.contrail.com', password='passwd')
        self.xmpp_agent.add_callback(self.notification_event)
        self.xmpp_agent.connect((controller_ip, 5269), use_tls=False, reattempt=False)
        self.xmpp_agent.process(block=False)
        self.ip_address = ip_address
        self.encapsulations = ['gre', 'udp']
        self.vee_list = []
        self.routing_table = []
        self.networks = ['blue', 'red']
        self.network_labels = {'blue' : '10', 'red' : '20'}
        self.ovs = OVS(self.networks)


    def notification_event(self, info):
        if info.item_id:
            parts = info.item_id.split(':')
            nlri = parts[0]
            next_hop = parts[2]
            self.remove_entry_from_routing_table(nlri=nlri, next_hop=next_hop)
        else:
            entry = [info.nlri, info.next_hop, info.label]
            self.routing_table.append(entry)
            self.ovs.addTunnelIntf(info.network, info.next_hop, info.label, info.nlri)

    def remove_entry_from_routing_table(self, nlri, next_hop):
        for entry in self.routing_table:
            if entry[0] == nlri and entry[1] == next_hop:
                entry_to_remove = entry

        self.routing_table.remove(entry_to_remove)

    def print_routing_table(self):
        content = '\n\n####\t'+ self.xmpp_agent.client_jid + '\t####'
        content += '\n####\tRouting Information Base\t####'
        content += "\nNLRI\t\tNEXTHOP\t\tLABEL\n"
        for e in self.routing_table:
            content += "{}\t{}\t{}\n".format(e[0], e[1], e[2])
        logger.info(content)

    def xmpp_session_started(self):
        return self.xmpp_agent.session_started

    def create_vee(self, identifier, network, ip_addr):
        if self.validate_create_params(identifier, network, ip_addr):
            logger.info("Creating new Virtual Execution Environment..")
            vee = Vee(identifier, network, ip_addr)
            self.attach_vee(vee)
            self.vee_list.append(vee)

    def validate_create_params(self, identifier, network, ip_addr):
        if network in self.networks:
            return False
        return True

    def wait_for_session_started(self):
        while not self.xmpp_session_started():
            pass

    def attach_vee(self, vee):
        self.wait_for_session_started()
        self.ovs.addHost(vee.identifier, vee.ip_address, vee.network)
        if not self.is_already_subscribed(vee.network):
            self.xmpp_agent.initial_subscribe(vee.network)
        pub_info = self.get_publish_info(vee)
        time.sleep(1)
        self.routing_table.append([vee.ip_address, 'localhost', pub_info.label])
        self.xmpp_agent.publish(vee.network, pub_info)
        vee.attached = True

    def detach_vee(self, vee):
        item_id = vee.ip_address + ":1:" + self.ip_address
        self.remove_entry_from_routing_table(vee.ip_address, 'localhost')
        self.xmpp_agent.retract(item_id, vee.network)
        vee.attached = False
        if not self.is_already_subscribed(vee.network):
            self.xmpp_agent.unsubscribe(vee.network)

    def list_vee(self):
        logger.info("Currently associated VEEs:\n")
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            vee.info()

    def ovs_cli(self):
        self.ovs.cli()

    def enter_vee(self):
        identifier = raw_input("Type identifier of VEE..\n")
        vee = self.get_vee(identifier)
        if vee:
            vee.console()
        else:
            logger.warn("No VEE with specified identifier!")

    def delete_vee(self, identifier):
        vee = self.get_vee(identifier)
        if vee in self.vee_list:
            self.vee_list.remove(vee)
            self.detach_vee(vee)

    def detach_all_vee(self):
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            self.detach_vee(vee)


    def get_vee(self, identifier):
        for i in range(0, len(self.vee_list)):
            vee = self.vee_list[i]
            if vee.identifier == identifier:
                return vee

    def shutdown(self):
        logger.info("Shutting vRouter down..")
        self.detach_all_vee()
        self.xmpp_agent.disconnect()
        self.ovs.stop()

    def get_publish_info(self, vee):
        nlri = vee.ip_address
        label = self.network_labels[vee.network]
        item_id = nlri + ":1:" + self.ip_address
        publish_info = PubInfo(item_id, nlri, str(label), self.ip_address, self.encapsulations)
        return publish_info

    def is_already_subscribed(self, network):
        for vee in self.vee_list:
            if vee.network == network:
                return True
        return False




if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    if not len(sys.argv) > 1:
        logger.error("Too few arguments")

    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    jid = config.get('general', 'jid')
    vrouter_ip = config.get('general', 'vrouter.ip')
    controller_ip = config.get('general', 'controller.ip')


    vrouter = VRouterMock(jid, vrouter_ip, controller_ip)

    while not vrouter.xmpp_session_started():
        time.sleep(1)

    os.system('clear')
    while True:
        print ("""
                            Console of vRouter {}..

                            1.Create a new VM
                            2.List already connected VM
                            3.Enter VM console
                            4.Delete VM
                            5.Shutdown vRouter
                            6.Dump routing table
                            """)
        option = raw_input("Choose action from list above..\n")

        if option == "1":
            identifier = raw_input("Type identifier of new VM..\n")
            network = raw_input("Type a network the VM should be attached to..\n")
            address = raw_input("Type an IP address of VM\n")
            vrouter.create_vee(identifier=identifier, network=network, ip_addr=address)
        elif option == "2":
            vrouter.list_vee()
        elif option == "3":
            vrouter.ovs_cli()
        elif option == "4":
            identifier = raw_input("Type identifier of VM to delete..\n")
            vrouter.delete_vee(identifier)
        elif option == "5":
            vrouter.shutdown()
            break
        elif option == "6":
            vrouter.print_routing_table()












