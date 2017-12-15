import sys
sys.path.insert(0, "/home/autonet/onos-dev/vrouter-client-py")
from vrouter import VRouterMock
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

vrouter1 = VRouterMock("agent1@vnsw.contrailsystems.com", "127.0.0.1", "127.0.0.1")
