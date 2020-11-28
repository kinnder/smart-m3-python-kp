from smart_m3.m3_kp import *

node = KP("Insert_ontology_node")
ss_handle = ("X", (TCPConnector, ("127.0.0.1", 10010)))
node.join(ss_handle)

ins = node.CreateInsertTransaction(ss_handle)
ins.send("tutorial_ontology.owl", encoding = "RDF-XML")
node.CloseInsertTransaction(ins)
node.leave(ss_handle)