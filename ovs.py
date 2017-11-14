#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

setLogLevel( 'info' )

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

        return net

    def addHost(self, name, ip, network):
        h = self.ovs.addHost(name, ip=ip)
        sw = self.nw_sw[network]
        self.ovs.addLink(h, sw)

    def addTunnelIntf(self, network, next_hop, label):
        sw = self.nw_sw[network]
        print sw
        output = sw.cmd(
            'ovs-vsctl add-port {} {}-gre{} -- set interface {}-gre{} type=vxlan options:key={} options:remote_ip={}'.format(
                sw.name, sw.name, label, sw.name,  label, label, next_hop))
        print output
        sw.cmdPrint('ovs-vsctl show')

    def stop(self):
        self.ovs.stop()

    def cli(self):
        CLI(self.ovs)