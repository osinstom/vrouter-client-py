"""
DESCRIPTION:

net0: 10.0.0.0/24

STEP 1) 1 vRouter. 3 VEEs. Each of VEEs subscribes (one by one) to the same network "net0" and publishes reaachability information to controller. 
STEP 2) One of the VEEs retract reachability info. All the others subscribers are notified.
STEP 3) The same VEE unsubscribes from "net0".


RESULTS:

STEP 1) Controller side: "net0" list should contain 3 VEEs subscribed. 
        vRouter side: "all VEEs should be notified"

"""

from vrouter import VRouterMock
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

vrouter1 = VRouterMock("agent1@vnsw.contrailsystems.com", "192.168.121.5")
vrouter2 = VRouterMock("agent2@vnsw.contrailsystems.com", "192.168.121.6")
vrouter1.create_vee('vm1', 'net0', '10.0.0.1')
vrouter1.create_vee('vm2', 'net0', '10.0.0.2')
vrouter2.create_vee('vm3', 'net0', '10.0.0.3')
time.sleep(3)

vrouter1.print_routing_table()
vrouter2.print_routing_table()

vrouter1.delete_vee('vm1')

time.sleep(3)
vrouter1.print_routing_table()
vrouter2.print_routing_table()