import sys
sys.path.insert(0, "/home/autonet/onos-dev/vrouter-client-py")
from vrouter import VRouterMock, PubInfo
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

vrouter1 = VRouterMock("agent1@vnsw.contrailsystems.com", "127.0.0.1", "127.0.0.1")
vrouter1.wait_for_session_started()
vrouter1.xmpp_agent.initial_subscribe("blue")
time.sleep(1)
nlri = '10.0.0.1'
label = '20'
next_hop = '127.0.0.1'
mac_address = "00:00:00:00:00:01"
item_id = vrouter1.generate_item_id(next_hop, "blue", nlri, mac_address)

encapsulations = ['gre', 'udp', 'vxlan']

pub_info = PubInfo(item_id, mac_address, nlri, label, next_hop, encapsulations)
vrouter1.xmpp_agent.publish_evpn('blue', pub_info)
time.sleep(3)
vrouter1.xmpp_agent.retract(item_id, 'blue')
time.sleep(1)
vrouter1.xmpp_agent.disconnect()