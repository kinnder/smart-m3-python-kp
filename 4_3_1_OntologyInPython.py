from smart_m3.m3_kp import *
from smart_m3.RDFTransactionList import *
import uuid

NS = "http://sm3-tut/Ontology.owl#"

class PushKP(KP):
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4()) + "_PushKP")
        self.ss_handle = ("X", (TCPConnector, (server_ip, server_port)))

    def join_sib(self):
        self.join(self.ss_handle)

    def leave_sib(self):
        self.leave(self.ss_handle)

    def createOntologyStructure(self):
        t = RDFTransactionList()
        t.add_Class(NS + "Thing")
        t.add_subClass(NS + "Device", NS+"Thing")
        t.add_subClass(NS + "MotionSensor", NS + "Device",)
        t.add_subClass(NS + "Lamp", NS + "Device", )

        i1 = self.CreateInsertTransaction(self.ss_handle)
        i1.send(t.get())
        self.CloseInsertTransaction(i1)

    def createInstances(self):
        t = RDFTransactionList()

        ms1 = NS + "MotionSensor_living_room_1"
        t.setType(ms1, NS + "MotionSensor")
        t.add_literal(ms1, NS + "hasMovement", "false")

        l1 = NS + "Lamp_living_room_1"
        t.setType(l1, NS + "Lamp")
        t.add_literal(l1, NS + "hasState", "false")

        i1 = self.CreateInsertTransaction(self.ss_handle)
        i1.send(t.get())
        self.CloseInsertTransaction(i1)

pd = PushKP("127.0.0.1", 10010)
pd.join_sib()
pd.createOntologyStructure()
pd.createInstances()
pd.leave_sib()