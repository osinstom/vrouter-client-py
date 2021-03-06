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
next_hop = '192.168.121.3'
item_id = nlri + ":1:" + next_hop
encapsulations = ['gre', 'udp', 'vxlan']

pub_info = PubInfo(item_id, nlri, label, next_hop, encapsulations)
vrouter1.xmpp_agent.publish('blue', pub_info)
time.sleep(3)
vrouter1.xmpp_agent.retract(item_id, 'green')
time.sleep(5)
vrouter1.xmpp_agent.disconnect()