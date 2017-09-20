from sleekxmpp import ClientXMPP, XMLStream, Iq
import time
import xml.etree.ElementTree
import logging

logger = logging.getLogger(__name__)

class VRouterMock(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.stream_header = "<stream:stream to='%s' %s %s %s %s %s>" % (
            self.boundjid.host,
            "from='agent@vnsw.contrailsystems.com/other-peer'" ,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")

        self.add_event_handler("connected", self.connected)
        self.add_event_handler("session_start", self.session_start, threaded=True)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3

    def start_stream_handler(self, xml):
        self.event('session_start')

    def connected(self, event):
        print 'CONNECTED !'

    def session_start(self, event):
        print 'Session started'
        self.initial_subscribe()
        time.sleep(3)
        self.publish_bgp_info()
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
        self.send_raw(subscribe_packet, now=True)

    def publish_bgp_info(self):
        bgp_info = open('testdata/pubsub.xml', 'r').read()
        self.send_raw(bgp_info, now=True)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()



if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    client = VRouterMock(jid='bgp.contrail.com', # JID of XMPP server
                         password='passwd')

    client.connect(('127.0.0.1', 5269), use_tls=False)
    client.process(block=True)

    # xmpp = XMLStream(host='127.0.0.1', port=5269)
    #
    # # pubsub_data = xml.etree.ElementTree.parse('testdata/pubsub.xml').getroot()
    # # xmlstr = xml.etree.ElementTree.tostring(xml.etree.ElementTree.tostring(pubsub_data, encoding='utf8', method='xml'))
    #
    # str = open('testdata/pubsub.xml', 'r').read()
    # print str
    #
    # if xmpp.connect(host='127.0.0.1', port=5269, use_tls=False):
    #
    #     ifrom = 'agent@vnsw.contrailsystems.com/other-peer'
    #     ito = 'bgp.contrail.com'
    #
    #
    #
    #     xmpp.stream_header= "<stream:stream " \
    #                     "from='{}' " \
    #                     "to='{}' " \
    #                     "version='1.0' " \
    #                     "xml:lang='en' " \
    #                     "xmlns='jabber:client' " \
    #                     "xmlns:stream='http://etherx.jabber.org/streams'>".format(ifrom, ito)
    #
    #     xmpp.stream_footer = "</stream:stream>"
    #
    #     iq = Iq(sfrom="agent@contrail.com", sto="controller@contrail.com")
    #     xmpp.send_queue.put(iq)
    #     xmpp.send_queue.put(str)
    #     xmpp.process(block=True)
    #     xmpp.send_queue.put(str)
    #
    #     # iq = xmpp.make_iq(id="req1", ifrom="agent@contrail.com", ito="controller@contrail.com")
    #     # xmpp.send_queue.put(iq)
    #     print 'connected'
    #
    #     # xmpp.send_presence()
    #
    #     # iq.send(now=True)
    #     # time.sleep(1)
    #     # iq.send(now=True)
    #     # xmpp.send_raw(str, now=True)
    #     # time.sleep(1)
    #     # xmpp.send_raw(str, now=True)
    #     # xmpp.send_raw(str, now=True)
    #     while True:
    #         'dds'





