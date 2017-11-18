#!/usr/bin/python



def get_ports(switch):
    output = switch.cmd("ovs-vsctl list-ports {}".format(switch.name))
    output = output.replace('\r', '')
    splitted = output.split('\n')
    ports = [x for x in splitted if x]
    print ports
    return ports


def get_vxlan_ports_number(sw):
    vxlan_ports = get_vxlan_ports(sw)
    return len(vxlan_ports)


def get_vxlan_ports(sw):
    all_ports = get_ports(sw)
    vxlan_ports = [x for x in all_ports if 'vxlan' in x]
    return vxlan_ports


def get_vxlan_port_number(sw, vxlan_port_id):
    all_ports = get_ports(sw)
    port_number = all_ports.index(vxlan_port_id)
    return port_number