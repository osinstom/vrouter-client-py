from sleekxmpp import ClientXMPP, XMLStream
import time
import xml.etree.ElementTree


xmpp = XMLStream(host='127.0.0.1', port=5269)

# pubsub_data = xml.etree.ElementTree.parse('testdata/pubsub.xml').getroot()
# xmlstr = xml.etree.ElementTree.tostring(xml.etree.ElementTree.tostring(pubsub_data, encoding='utf8', method='xml'))

str = open('testdata/pubsub.xml', 'r').read()
print str

if xmpp.connect(host='127.0.0.1', port=5269, use_tls=False):

    ifrom = 'agent@vnsw.contrailsystems.com/other-peer'
    ito = 'bgp.contrail.com'



    xmpp.stream_header= "<stream:stream " \
                        "from='{}' " \
                        "to='{}' " \
                        "version='1.0' " \
                        "xml:lang='en' " \
                        "xmlns='jabber:client' " \
                        "xmlns:stream='http://etherx.jabber.org/streams'>".format(ifrom, ito)
    xmpp.process(block=True)
    print 'connected'

    # xmpp.send_presence()
    # iq = xmpp.make_iq(id="req1", ifrom="agent@contrail.com", ito="controller@contrail.com")
    # iq.send(now=True)
    # time.sleep(1)
    # iq.send(now=True)
    # xmpp.send_raw(str, now=True)
    # time.sleep(1)
    # xmpp.send_raw(str, now=True)
    # xmpp.send_raw(str, now=True)
    while True:
        'dds'
    # xmpp.process(block=True)
    # xmpp.disconnect()




