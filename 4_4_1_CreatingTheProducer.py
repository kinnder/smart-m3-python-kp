from smart_m3.m3_kp import *
import uuid

NS = "http://sm3-tut/Ontology.owl#"

class ProducerKP(KP):
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4())+"_ProducerKP")
        self.ss_handle = ("X", (TCPConnector, (server_ip,server_port)))

    def join_sib(self):
        self.join(self.ss_handle)

    def leave_sib(self):
        self.leave(self.ss_handle)

    def insert(self, triples):
        ins = self.CreateInsertTransaction(self.ss_handle)
        ins.send(triples)
        self.CloseInsertTransaction(ins)

    def remove(self, triples):
        rem = self.CreateRemoveTransaction(self.ss_handle)
        rem.remove(triples)
        self.CloseRemoveTransaction(rem)

    def update(self, i_trip, r_trip):
        # Update = Insert + Remove
        upd = self.CreateUpdateTransaction(self.ss_handle)
        upd.update(i_trip, "RDF-M3", r_trip, "RDF-M3")
        self.CloseUpdateTransaction(upd)

pd = ProducerKP("127.0.0.1", 10010)
pd.join_sib()

while True:
    i = input("\nSet motion sensor state"+
    "\n0 : No Movement" +
    "\n1 : Movement" +
    "\nexit : Exit program\n")

    if i == "1":
        print("Setting state to True")
        ins_trip = [Triple(
            URI(NS+"MotionSensor_living_room_1"),
            URI(NS+"hasMovement"),
            Literal("true"))]
        rem_trip = [Triple(
            URI(NS+"MotionSensor_living_room_1"),
            URI(NS+"hasMovement"),
            Literal("false"))]
        pd.update(ins_trip, rem_trip)

    elif i == "0":
        print("Setting state to False")
        ins_trip = [Triple(
            URI(NS+"MotionSensor_living_room_1"),
            URI(NS+"hasMovement"),
            Literal("false"))]
        rem_trip = [Triple(
            URI(NS+"MotionSensor_living_room_1"),
            URI(NS+"hasMovement"),
            Literal("true"))]
        pd.update(ins_trip, rem_trip)

    elif i.lower() == "exit":
        break

pd.leave_sib()
