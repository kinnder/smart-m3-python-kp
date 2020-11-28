from smart_m3.m3_kp import *
import uuid
import subprocess
import platform

NS = "http://sm3-tut/Ontology.owl#"

class OnChangeHandler:
    def __init__(self, node):
        self.node = node

    def handle(self, added, removed):
        self.node.show_devices()

class ConsumerKP(KP):
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4()) + "_Consumer")
        self.ss_handle = ("X", (TCPConnector, (server_ip, server_port)))
        self.subscriptions = []

    def join_sib(self):
        self.join(self.ss_handle)

    def leave_sib(self):
        for subscription in self.subscriptions:
            self.CloseSubscribeTransaction(subscription)
        self.leave(self.ss_handle)

    def update(self, i_trip, r_trip):
        upd = self.CreateUpdateTransaction(self.ss_handle)
        upd.update(i_trip, "RDF-M3", r_trip, "RDF-M3")
        self.CloseUpdateTransaction(upd)

    def create_subscription(self, trip):
        st = self.CreateSubscribeTransaction(self.ss_handle)
        initial_results = st.subscribe_rdf(trip, OnChangeHandler(self))
        self.subscriptions.append(st)

    def sparql_query(self, sparql):
        PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ns: <http://sm3-tut/Ontology.owl#>
"""
        q = PREFIXES+sparql
        qt = self.CreateQueryTransaction(self.ss_handle)
        results = qt.sparql_query(q)
        self.CloseQueryTransaction(qt)

        return results

    def get_devices(self):
        sparql = """SELECT ?device ?device_type ?attribute ?state
    WHERE {?device_type rdfs:subClassOf ns:Device
    .
        ?device rdf:type ?device_type
        .
            ?device ?attribute ?state
            FILTER(?attribute != rdf:type)}
"""
        results = self.sparql_query(sparql)

        devices = []
        for result_device in results:
            device = {"attribute":{}}
            for trip in result_device:

                if trip[0] == "attribute":
                    lastAttrib = trip[2]

                elif trip[0] == "state":
                    device["attribute"][lastAttrib] = trip[2]

                else:
                    device[trip[0]] = trip[2]

            devices.append(device)

        return devices

    def create_device_subscriptions(self, devices):
        for device in devices:
            trip = [Triple(URI(device["device"]),
                           None,
                           None)]
            self.create_subscription(trip)

    def show_devices(self):
        subprocess.Popen("cls"
                         if platform.system() == "Windows"
                         else "clear", shell = True)
        print("Current status (type ’exit’ to quit):")
        devices = self.get_devices()
        for device in devices:
            print("\nDevice: "+device["device"].replace(NS,""))
            for attr, state in device["attribute"].iteritems():
                print("\t", attr.replace(NS, ""), ": ", state)
        return devices


pd = ConsumerKP("127.0.0.1", 10010)
pd.join_sib()
pd.create_device_subscriptions(pd.show_devices())

while True:
    i = input("\nType \"exit\" to exit the program\n")

    if i.lower() == "exit":
        break

pd.leave_sib()