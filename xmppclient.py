from sleekxmpp import ClientXMPP, XMLStream, Iq
import logging
import time

logger = logging.getLogger(__name__)

class XmppClient(ClientXMPP):
    def __init__(self, client_jid, server_jid, password):
        self.session_started = False

        ClientXMPP.__init__(self, server_jid, password)
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

        self.jid_pattern = "%FROMJID%"
        self.node_pattern = "%NODEID%"

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
        packet = str(packet).replace(self.node_pattern, node)
        return packet

    def publish_bgp_info(self):
        bgp_info = open('testdata/pubsub.xml', 'r').read()
        self.send_xmpp(bgp_info)

    def message(self, msg):
        logger.info("XMPP Message received!")
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

        self.publish_bgp_info()

    def send_xmpp(self, packet):
        packet = self.prepare_xml(packet)
        self.send_raw(packet, now=True)

    def prepare_xml(self, packet):
        packet = str(packet).replace(self.jid_pattern, self.client_jid)
        return packet