from smart_m3.m3_kp import *
import uuid

NS = "http://sm3-tut/Ontology.owl#"

class MotionSensorHandler:
    def __init__(self, node):
        self.node = node

    def handle(self, added, removed):
        lamp_on = [Triple(
            URI(NS+"Lamp_living_room_1"),
            URI(NS+"hasState"),
            Literal("true"))]
        lamp_off = [Triple(
            URI(NS+"Lamp_living_room_1"),
            URI(NS+"hasState"),
            Literal("false"))]        

        for trip in added:
            if str(trip[2]) == "true":
                #update(TRIPLE_TO_INSERT,TRIPLE_TO_REMOVE)
                self.node.update(lamp_on, lamp_off)
                print("lamp turned on")
				

        for trip in removed:
            if str(trip[2] == "true"):
                self.node.update(lamp_off, lamp_on)
                print("lamp turned off")

				

class AggregatorKP(KP):
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4())+"_Aggregator")
        self.ss_handle = ("X", (TCPConnector, (server_ip,server_port)))

    def join_sib(self):
        self.join(self.ss_handle)

    def leave_sib(self):
        self.CloseSubscribeTransaction(self.st)
        self.leave(self.ss_handle)

    def update(self, i_trip, r_trip):
        upd = self.CreateUpdateTransaction(self.ss_handle)
        upd.update(i_trip, "RDF-M3", r_trip, "RDF-M3")

        self.CloseUpdateTransaction(upd)

    def create_subscription(self):
        trip = [Triple(
            URI(NS + "MotionSensor_living_room_1"),
            URI(NS + "hasMovement"),
            None)]
        self.st = self.CreateSubscribeTransaction(self.ss_handle)
        initial_results = self.st.subscribe_rdf(trip, MotionSensorHandler(self))
        print(initial_results)


pd = AggregatorKP("127.0.0.1", 10010)
pd.join_sib()
pd.create_subscription()

while True:
    i = input("\nType \"exit\" to exit the program\n")

    if i.lower() == "exit":
        break

pd.leave_sib()
