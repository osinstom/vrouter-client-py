from sleekxmpp import ClientXMPP
import xml.etree.ElementTree


xmpp = ClientXMPP('somejid@example.com', 'use_getpass')

pubsub_data = xml.etree.ElementTree.parse('testdata/pubsub.xml').getroot()
# xmlstr = xml.etree.ElementTree.tostring(xml.etree.ElementTree.tostring(pubsub_data, encoding='utf8', method='xml'))



if xmpp.connect(('127.0.0.1', 5269)):
    xmpp.send_xml(pubsub_data)
    # xmpp.process(block=True)





