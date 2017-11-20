#!/usr/bin/python

import logging
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import ovs_binding

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
        sw = self.nw_sw[network]

        ovs_binding.get_interfaces(sw)

        if not ovs_binding.is_vxlan_port_already_created(sw, next_hop, label):
            vxlan_port = len(ovs_binding.get_ports(sw)) + ovs_binding.PORT_OFFSET
            vxlan_port_id = '{}-vxlan{}-{}'.format(sw.name, str(ovs_binding.get_vxlan_ports_number(sw) + 1), label)
            output = sw.cmd(
                'ovs-vsctl add-port {} {} -- set interface {} type=vxlan options:key={} options:remote_ip={} ofport_request={}'.format(
                    sw.name, vxlan_port_id, vxlan_port_id,  label, next_hop, vxlan_port))
            print output

        dst_port = ovs_binding.get_vxlan_port_name_for_nexthop(sw, next_hop, label)

        sw.cmd(
            'sudo ovs-ofctl add-flow {} ip,nw_dst={},actions=output:{}'.format(sw.name, dst_ip, dst_port)
        )
        sw.cmdPrint('ovs-vsctl show')

    def stop(self):
        self.ovs.stop()

    def cli(self):
        CLI(self.ovs)

    def remove_routing_flow(self, ip_address, next_hop, network):
        sw = self.nw_sw[network]
        sw.cmd('ovs-ofctl del-flows {} "ip,nw_dst={}"'.format(sw.name, ip_address))
