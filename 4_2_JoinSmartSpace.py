from smart_m3.m3_kp import *
import uuid


class FirstKP(KP):
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4())+"_FirstKP")
        self.ss_handle = ("X", (TCPConnector, (server_ip, server_port)))

    def join_sib(self):
        self.join(self.ss_handle)

    def leave_sib(self):
        self.leave(self.ss_handle)


pd = FirstKP("127.0.0.1", 10010)
pd.join_sib()
pd.leave_sib()