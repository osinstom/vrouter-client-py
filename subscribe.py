from sleekxmpp import ClientXMPP
import xml.etree.ElementTree


xmpp = ClientXMPP('somejid@example.com', 'use_getpass')

# pubsub_data = xml.etree.ElementTree.parse('testdata/pubsub.xml').getroot()
# xmlstr = xml.etree.ElementTree.tostring(xml.etree.ElementTree.tostring(pubsub_data, encoding='utf8', method='xml'))

str = open('testdata/pubsub_pub.xml', 'r').read()
print str

if xmpp.connect(('127.0.0.1', 5269)):
    # xmpp.send_presence()
    xmpp.send_raw(str, now=True)
    # xmpp.process(block=True)





