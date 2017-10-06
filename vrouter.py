from sleekxmpp import ClientXMPP, XMLStream, Iq
import time
import xml.etree.ElementTree
import logging
import argparse, sys

from xmppclient import XmppClient

logger = logging.getLogger(__name__)

class VRouterMock():

    def __init__(self, client_jid):
        xmpp = XmppClient(client_jid=client_jid, server_jid='bgp.contrail.com', password='passwd')
        xmpp.connect(('127.0.0.1', 5269), use_tls=False)
        xmpp.process(block=True)


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    if not len(sys.argv) > 1:
        logger.error("Too few arguments")
    jid = sys.argv[1]
    vrouter = VRouterMock(jid)








