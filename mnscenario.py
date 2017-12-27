#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo


def emptyNet():
    NODE2_IP = '192.168.158.4'
    CONTROLLER_IP = '192.168.27.3'

    net = Mininet(topo=None,
                  build=False)

    # Initialize topology
    net.addController('c0',
                      controller=RemoteController,
                      ip=CONTROLLER_IP,
                      port=6633)

    # Add hosts and switches
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    s1 = net.addSwitch('s1')

    # Add links
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    net.start()

    s1.cmd(
        'ovs-vsctl add-port s1 vxlan1 -- set interface vxlan1 type=vxlan options:key=20 options:remote_ip={} ofport_request=20'.format(
            NODE2_IP))
    s1.cmdPrint('ovs-vsctl show')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    emptyNet()