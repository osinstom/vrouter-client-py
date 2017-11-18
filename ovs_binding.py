#!/usr/bin/python



def get_ports(switch):
    output = switch.cmd("ovs-vsctl list-ports {}".format(switch.name))
    print output