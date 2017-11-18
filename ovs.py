#!/usr/bin/python

import logging
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

setLogLevel( 'info' )

logger = logging.getLogger(__name__)

class OVS():

    def __init__(self, networks):
        self.nw_sw = {}
        self.ovs = self.start(networks)
        print "OVS initialized"

    def start(self, networks):
        net = Mininet(topo=None,
                      build=False)

        for idx, nw in enumerate(networks):
            sw = net.addSwitch('s' + str(idx+1))
            self.nw_sw[nw] = sw

        net.start()

        for switch in self.nw_sw.values():
            switch.cmd('ovs-ofctl add-flow {} arp,actions=flood'.format(switch.name))
            switch.cmd('ovs-ofctl add-flow {} ip,actions=flood'.format(switch.name))

        return net

    def addHost(self, name, ip, network):
        h = self.ovs.addHost(name)

        sw = self.nw_sw[network]
        link = self.ovs.addLink(h, sw)
        h.cmd('ifconfig {} {} up'.format(link.intf1, ip))
        sw.attach(link.intf2)

    def addTunnelIntf(self, network, next_hop, label, dst_ip):
        logger.info("Networks: " + str(self.nw_sw))
        logger.info("Network: " + str(network))
        sw = self.nw_sw[network]
        print sw
        vxlan_port = 45
        output = sw.cmd(
            'ovs-vsctl add-port {} {}-gre{} -- set interface {}-gre{} type=vxlan options:key={} options:remote_ip={} ofport_request={}'.format(
                sw.name, sw.name, label, sw.name,  label, label, next_hop, vxlan_port))
        print output
        sw.cmd(
            'sudo ovs-ofctl add-flow {} ip,nw_dst={},actions=output:{}'.format(sw.name, dst_ip, vxlan_port)
        )
        sw.cmdPrint('ovs-vsctl show')

    def stop(self):
        self.ovs.stop()

    def cli(self):
        CLI(self.ovs)