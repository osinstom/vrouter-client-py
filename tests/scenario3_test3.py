
import logging
import time
import sys
sys.path.insert(0, "/home/autonet/onos-dev/vrouter-client-py")
from vrouter import VRouterMock

logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

vrouter1 = VRouterMock("agent3@xmpp.org", "127.0.0.1", "127.0.0.1")
vrouter1.wait_for_session_started()
vrouter1.xmpp_agent.initial_subscribe("blue")
time.sleep(3)