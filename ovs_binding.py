#!/usr/bin/python

# port offset, OVS starts numbering ports from 2, so the 0 index will be port number 2
PORT_OFFSET = 2

class OvsIntf():
    def __init__(self, number, name, options):
        self.number = number
        self.name = name
        self.options = options

def get_interfaces(switch):
    intfs = []
    output = switch.cmd("ovs-vsctl --columns=name,ofport,options --format=table list Interface")
    print output.split('\n')
    lines = [x for x in output.split('\n') if switch.name in x]
    for line in lines:
        options = line[line.find('{')+1:line.find('}')]
        splitted_line = line.split()
        intf = OvsIntf(number=splitted_line[1], name=splitted_line[0], options=options)
        intfs.append(intf)

    return intfs

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
    port_number = all_ports.index(vxlan_port_id) + PORT_OFFSET
    return port_number


def is_vxlan_port_already_created(sw, next_hop_ip, label):
    intfs = get_interfaces(sw)
    for intf in intfs:
        if next_hop_ip in intf.options and label in intf.options:
            return True
    return False


def get_port_number_name_records(sw):
    output = sw.cmdPrint('ovs-ofctl show {}'.format(sw.name))
    records = dict()
    for line in output.split('\n'):
        if '(' in line and ')' in line and 'addr' in line:
            if not 'LOCAL' in line:
                splitted = line.split(': addr:')
            number, name = get_port_number_name_record(splitted[0])
            records[number] = name

    print str(records)
    return records


def get_port_number_name_record(param):
    splitted = param.split('(')
    number = splitted[0]
    name = splitted[1].replace(')', '')
    return number, name


def get_vxlan_port_name_for_nexthop(sw, next_hop, label):
    intfs = get_interfaces(sw)
    for intf in intfs:
        if next_hop in intf.options and label in intf.options:
            return intf.number