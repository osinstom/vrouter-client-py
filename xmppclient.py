from sleekxmpp import ClientXMPP, XMLStream, Iq
import logging
import time

logger = logging.getLogger(__name__)

class XmppClient(ClientXMPP):
    def __init__(self, client_jid, server_jid, password):
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

    def start_stream_handler(self, xml):
        self.event('session_start')

    def connected(self, event):
        print 'CONNECTED !'

    def session_start(self, event):
        print 'Session started'
        self.initial_subscribe()
        time.sleep(5)
        self.unsubscribe()
        # self.send_presence()
        # self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def initial_subscribe(self):
        subscribe_packet = open('testdata/pubsub_sub.xml', 'r').read()
        self.send_xmpp(subscribe_packet)

    def unsubscribe(self):
        unsubscribe_xml = open('testdata/unsubscribe.xml', 'r').read()
        self.send_xmpp(unsubscribe_xml)

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
        packet = str(packet).replace("%fromjid%", self.client_jid)
        return packet