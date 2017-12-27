from sleekxmpp import ClientXMPP, XMLStream, Iq, StanzaPath, Callback
import logging
from xml.etree import cElementTree as ET
import time
import xml.dom.minidom

from util import PubInfo, Observable

logger = logging.getLogger(__name__)

FROM_JID_PATTERN = "%FROMJID%"
TO_JID_PATTERN = "%TOJID%"
NODE_PATTERN = "%NODEID%"
ITEMID_PATTERN = "%ITEMID%"
NLRI_PATTERN = "%NLRI%"
MACADDR_PATTERN = "%MAC%"
IPADDR_PATTERN = "%IPADDRESS%"
NEXTHOP_PATTERN = "%NEXTHOP%"
LABEL_PATTERN = "%LABEL%"
ENCAPS_PATTERN = "%ENCAPS%"


class XmppClient(ClientXMPP, Observable):
    def __init__(self, client_jid, server_jid, password):
        self.session_started = False

        ClientXMPP.__init__(self, server_jid, password)
        Observable.__init__(self)

        self.auto_reconnect = False
        self.client_jid = client_jid
        self.stream_header = "<stream:stream to='%s' %s %s %s %s %s>" % (
            self.boundjid.host,
            "from='%s'" % self.client_jid,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")

        self.add_event_handler("connected", self.connected)
        self.add_event_handler("session_start", self.session_start, threaded=True)
        self.add_event_handler("message", self.message)

        self.register_handler(
            Callback('message',
                     StanzaPath('message'),
                     lambda msg: self.event('message', msg)))



    def start_stream_handler(self, xml):
        self.event('session_start')

    def connected(self, event):
        logger.info('VROUTER {} CONNECTED !'.format(self.client_jid))

    def session_start(self, event):
        logger.info("Session started")
        self.session_started = True
        self.session_started_event.set()

    def initial_subscribe(self, node):
        subscribe_packet = open('testdata/subscribe.xml', 'r').read()
        subscribe_packet = self.prepare_subscribe_xml(subscribe_packet, node)
        self.send_xmpp(subscribe_packet)

    def unsubscribe(self, node):
        unsubscribe_xml = open('testdata/unsubscribe.xml', 'r').read()
        unsubscribe_xml = self.prepare_subscribe_xml(unsubscribe_xml, node)
        self.send_xmpp(unsubscribe_xml)

    def prepare_subscribe_xml(self, packet, node):
        packet = str(packet).replace(NODE_PATTERN, node)
        return packet

    def publish(self, publish_to, publish_info):
        bgp_info = open('testdata/publish.xml', 'r').read()
        bgp_info = self.prepare_publish(bgp_info, publish_info, publish_to)
        self.send_xmpp(bgp_info)

    def publish_evpn(self, node, publish_info):
        info = open('testdata/publish_evpn.xml', 'r').read()
        evpn_info = self.prepare_evpn_publish(info, publish_info, node)
        self.send_xmpp(evpn_info)

    def message(self, msg):
        logger.info("XMPP Message received!")
        payload = msg.get_payload()
        xml = payload[0]

        node = xml.find('./items').attrib['node']
        item = xml.find('.//items/item')

        if item:
            self.handle_event_notification(item, node)
        else:
            self.handle_retract_notification(xml)

    def handle_event_notification(self, item, node):
        elements = list(item.iter())

        for el in elements:
            if 'nlri' in str(el.tag):
                nlri = el.text
            if 'next-hop' in str(el.tag):
                next_hop = el.text
            if 'label' in str(el.tag):
                label = el.text

        self.fire(item_id=None, nlri=nlri, next_hop=next_hop, label=label, encapsulations=[], network=node)

    def handle_retract_notification(self, xml):
        items = xml.find('.//items')
        node_id = items.get('node')
        retract = xml.find('.//items/retract')
        item_id = retract.get('id')
        self.fire(item_id=item_id, node_id=node_id)

    def send_xmpp(self, packet):
        packet = self.prepare_xml(packet)
        self.send_raw(packet, now=True)

    def prepare_xml(self, packet):
        packet = str(packet).replace(FROM_JID_PATTERN, self.client_jid)
        return packet

    def prepare_publish(self, packet, info, node_id):
        packet = str(packet).replace(NODE_PATTERN, node_id)
        packet = str(packet).replace(ITEMID_PATTERN, info.item_id)
        packet = str(packet).replace(NLRI_PATTERN, info.nlri)
        packet = str(packet).replace(NEXTHOP_PATTERN, info.next_hop)
        packet = str(packet).replace(LABEL_PATTERN, info.label)
        tunnel_encaps_start = '<tunnel-encapsulation>'
        tunnel_encaps_end = '</tunnel-encapsulation>'
        encaps_data = ''
        for e in info.encapsulations:
            record = tunnel_encaps_start + e + tunnel_encaps_end
            encaps_data += record + '\n'

        packet = str(packet).replace(ENCAPS_PATTERN, encaps_data)
        return packet

    def retract(self, item_id, node_id):
        retract_packet = open('testdata/retract.xml', 'r').read()
        retract_packet = str(retract_packet).replace(ITEMID_PATTERN, item_id)
        retract_packet = str(retract_packet).replace(NODE_PATTERN, node_id)
        self.send_xmpp(retract_packet)

    def prepare_evpn_publish(self, packet, publish_info, node):
        packet = str(packet).replace(NODE_PATTERN, node)
        packet = str(packet).replace(ITEMID_PATTERN, publish_info.item_id)
        packet = str(packet).replace(IPADDR_PATTERN, publish_info.nlri)
        packet = str(packet).replace(NEXTHOP_PATTERN, publish_info.next_hop)
        packet = str(packet).replace(LABEL_PATTERN, publish_info.label)
        packet = str(packet).replace(MACADDR_PATTERN, publish_info.mac_address)
        return packet