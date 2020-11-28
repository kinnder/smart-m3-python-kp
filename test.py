from smart_m3.m3_kp import *

from random import choice

from datetime import datetime

import os
import shutil

import time

SIB_IP = "127.0.0.1"
#SIB_IP = "192.168.1.130"
SIB_PORT = 10010

SIB_LOG = "experiments.txt"
KP_LOG = "kp.txt"

def generate_word(length):
	return "".join(choice(str.lower) for i in range(length))

def write_file(filename, string):
    with open(filename, "a") as f:
        f.write(string)
        
def clear_file(filename):
    with open(filename, "w+") as f:
        f.truncate()
        
def save_file(filename):
    shutil.copyfile(filename, filename + "-" + datetime.now().strftime("%y%m%d_%H-%M") + ".txt")

def log_db_size():
    po = os.stat("../X-po2s.db").st_size
    so = os.stat("../X-so2p.db").st_size
    sp = os.stat("../X-sp2o.db").st_size
    size_str = "{0} {1} {2}\n".format(po, so, sp)
    with open("db_size.txt", "a") as f:
        f.write(size_str)
    

class KnowledgeProcessor(KP):
    def __init__(self, sib_ip="127.0.0.1", sib_port=10010, kp_name="test"):
        KP.__init__(self, kp_name)
        self.ss_handle = ("X", (TCPConnector, (sib_ip,
                                               sib_port)))
    
    def join_sib(self):
        self.join(self.ss_handle)
        
    def leave_sib(self):
        self.leave(self.ss_handle)
        		
    def _query_triples(self, triples):
        qt = self.CreateQueryTransaction(self.ss_handle)
        t = qt.rdf_query(triples)
        #print "queried triples count:", len(t)
        self.CloseQueryTransaction(qt)
        return t

    def _sparql_query(self, sparql):
        PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/02/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            """
        q = PREFIXES+sparql
        #q = PREFIXES+sparql

        qt = self.CreateQueryTransaction(self.ss_handle)
        result = qt.sparql_query(q)
        self.CloseQueryTransaction(qt)

        return result
    
    def _insert_triples(self, triples):
        ins = self.CreateInsertTransaction(self.ss_handle)
        ins.send(triples, confirm = True)
        self.CloseInsertTransaction(ins)
                        
    def _update_triples(self, triples_ins, triples_rem):
        upd = self.CreateUpdateTransaction(self.ss_handle)
        upd.update(triples_ins, "RDF-M3", triples_rem, "RDF-M3", confirm = True)
        self.CloseUpdateTransaction(upd)

    def _remove_triples(self, triples):
        rem = self.CreateRemoveTransaction(self.ss_handle)
        rem.remove(triples)
        self.CloseRemoveTransaction(rem)
        
    def remove_all_triples(self):
        self._remove_triples(Triple(None, None, None))
        
    def insert_remove_triples(self, number, remove=True):
        triples = []
        word_length = 10
        for i in range(number):
            triple = Triple(URI(generate_word(word_length)), 
            URI(generate_word(word_length)), URI(generate_word(word_length)))
            triples.append(triple)
        #print triples	
        self._insert_triples(triples)
        
        if remove:
            self._remove_triples(triples)
		
    def insert_remove_fixed_triples(self, number, remove=False):
        triples = []
        word_length = 10
        if True:
            subject = generate_word(word_length)
        for i in range(number):
            triple = Triple(URI(subject), 
            URI(generate_word(word_length)), URI(generate_word(word_length)))
            triples.append(triple)
        #print triples	
        self._insert_triples(triples)
        
        if remove:
            self.remove_fixed_triples(subject)

        return subject
     
    def remove_fixed_triples(self, tsubject = None, tpredicate = None, tobject = None):
        triple = [Triple(URI(tsubject) if tsubject else None, 
                    URI(tpredicate) if tpredicate else None,
                    URI(tobject) if tobject else None)]
        self._remove_triples(triple)

    def test_sparql(self):
        query = """SELECT ?a ?b ?c
                    WHERE {{ ?a ?b ?c}} 
                """
        query_result = self._sparql_query(query)
        print(query_result)


    def experiment_query_sparql(self, name = None):
        def parent_timeslot_sparql(timeslot_uuid):
            query = """SELECT ?a
                        WHERE {{ ?a <http://www.cs.karelia.ru/smartroom#nextTimeslot> <{0}> }} 
                    """
            query = query.format(timeslot_uuid)
            query_result = self._sparql_query(query)
            for i in query_result:
                return i[0][2]
                
        if name == None:
            print("Enter name to search:")
            name = str(input())

        query = """SELECT ?t
                    WHERE {{ ?p <http://xmlns.com/foaf/0.1/name> "{0}".
				?t <http://www.cs.karelia.ru/smartroom#timeslotPerson> ?p}} 
                """
        query = query.format(name)
        query_result = self._sparql_query(query)

        for i in query_result:
            t_id = i[0][2]
            p_id = parent_timeslot_sparql(t_id)
            while p_id != None:
                t_id = p_id
                p_id = parent_timeslot_sparql(t_id)

            query = """SELECT ?at
                        WHERE {{ ?s <http://www.cs.karelia.ru/smartroom#firstTimeslot> <{0}>.
				?s <http://www.cs.karelia.ru/smartroom#sectionTitle> ?st.
				?a <http://www.cs.karelia.ru/smartroom#hasSection> ?s.
				?a <http://www.cs.karelia.ru/smartroom#activityTitle> ?at}} 
                    """
            query = query.format(t_id)
            query_result = self._sparql_query(query)
            sec_id = query_result[0][0][2]

    def experiment_query_sparql2(self, name = None):
        if name == None:
            print("Enter name to search:")
            name = str(input())

        query = """SELECT ?at
                    WHERE {{ ?p <http://xmlns.com/foaf/0.1/name> "{0}".
                ?t <http://www.cs.karelia.ru/smartroom#timeslotPerson> ?p.
                ?td <http://www.cs.karelia.ru/smartroom#nextTimeslot> ?t.
                ?tc <http://www.cs.karelia.ru/smartroom#nextTimeslot> ?td.
                ?tb <http://www.cs.karelia.ru/smartroom#nextTimeslot> ?tc.
                ?ta <http://www.cs.karelia.ru/smartroom#nextTimeslot> ?tb.
                ?s <http://www.cs.karelia.ru/smartroom#firstTimeslot> ?ta.
				?s <http://www.cs.karelia.ru/smartroom#sectionTitle> ?st.
				?a <http://www.cs.karelia.ru/smartroom#hasSection> ?s.
				?a <http://www.cs.karelia.ru/smartroom#activityTitle> ?at}} 
                    """
        query = query.format(name)
        query_result = self._sparql_query(query)
        print(query_result)

    def experiment_query_template(self, name = None):
           def parent_timeslot_template(timeslot_uuid):
               query_result = self._query_triples([Triple(None, URI("http://www.cs.karelia.ru/smartroom#nextTimeslot"), URI(timeslot_uuid))])
               if query_result != []:
                   return query_result[0][0]
               else:
                   return None
                   
           if name == None:
               print("Enter name to search:")
               name = str(input())

           query = """SELECT ?t
                       WHERE {{ ?p <http://xmlns.com/foaf/0.1/name> "{0}".
                                   ?t <http://www.cs.karelia.ru/smartroom#timeslotPerson> ?p}} 
                   """
           person_uuid = self._query_triples([Triple(None, URI("http://xmlns.com/foaf/0.1/name"), Literal(name))])[0][0]
           query_result = self._query_triples([Triple(None, URI("http://www.cs.karelia.ru/smartroom#timeslotPerson"), URI(person_uuid))])

           for i in query_result:
               t_id = i[0]
               p_id = parent_timeslot_template(t_id)
               while p_id != None:
                   t_id = p_id
                   p_id = parent_timeslot_template(t_id)

               query = """SELECT ?at
                           WHERE {{ ?s <http://www.cs.karelia.ru/smartroom#firstTimeslot> <{0}>.
                                   ?s <http://www.cs.karelia.ru/smartroom#sectionTitle> ?st.
                                   ?a <http://www.cs.karelia.ru/smartroom#hasSection> ?s.
                                   ?a <http://www.cs.karelia.ru/smartroom#activityTitle> ?at}} 
                       """
               sec_uuid = self._query_triples([Triple(None, URI("http://www.cs.karelia.ru/smartroom#firstTimeslot"), URI(t_id))])[0][0]
               act_uuid = self._query_triples([Triple(None, URI("http://www.cs.karelia.ru/smartroom#hasSection"), URI(sec_uuid))])[0][0]
               act_title = self._query_triples([Triple(URI(act_uuid), URI("http://www.cs.karelia.ru/smartroom#activityTitle"), None)])[0][2]

    def experiment_query_example(self):
        clear_file(KP_LOG)
        print("Enter name to search:")
        name = str(input())
        rng = 30
        print("sprql query example")
        for i in range(rng):
            print("iteration " + str(i))
            write_file(KP_LOG, "sprql query example")
            start_time = datetime.now()
            self.experiment_query_sparql(name)
            time_elapsed = datetime.now()
            query_sparql_time = int(round((time_elapsed - start_time).total_seconds()*1000))
            write_file(KP_LOG, "sparql {}\n".format(query_sparql_time))
        print("sprql query 2 example")
        for i in range(rng):
            print("iteration " + str(i))
            write_file(KP_LOG, "sprql2 query example")
            start_time = datetime.now()
            self.experiment_query_sparql(name)
            time_elapsed = datetime.now()
            query_sparql_time = int(round((time_elapsed - start_time).total_seconds()*1000))
            write_file(KP_LOG, "sparql2 {}\n".format(query_sparql_time))
            
        print("tmplt query example")
        for i in range(rng):
            print("iteration " + str(i))
            write_file(KP_LOG, "tmplt query example")
            start_time = datetime.now()
            self.experiment_query_template(name)
            time_elapsed = datetime.now()
            query_template_time = int(round((time_elapsed - start_time).total_seconds()*1000))
            write_file(KP_LOG, "template {}\n".format(query_template_time))

    def experiment_insert_remove(self):
        self.remove_all_triples()
        clear_file(SIB_LOG)
        clear_file(KP_LOG)
        ranges = [1000] + range(0, 35001, 5000)[1:]
        #ranges = range(30000, 35001, 5000)
        for i in ranges:
            print("Working with " + str(i) + " triples")
            write_file(SIB_LOG, "Working with " + str(i) + " triples\n")
            write_file(KP_LOG, "Working with " + str(i) + " triples\n")
            for j in range(50):
                print("iteration " + str(j))
                start_time = datetime.now()
                kp.insert_remove_triples(i, False)
                insert_time_elapsed = datetime.now()
                kp._query_triples(Triple(None, None, None))
                query_time_elapsed = datetime.now()
                kp.remove_all_triples()
                remove_time_elapsed = datetime.now()
                insert_time = int(round((insert_time_elapsed - start_time).total_seconds()*1000))
                query_time = int(round((query_time_elapsed - insert_time_elapsed).total_seconds()*1000))
                remove_time = int(round((remove_time_elapsed - query_time_elapsed).total_seconds()*1000))
                write_file(KP_LOG, "insert {}\n".format(insert_time))
                write_file(KP_LOG, "query {}\n".format(query_time))
                write_file(KP_LOG, "remove {}\n".format(remove_time))
                #print "insert: " + str(int((insert_time-start_time).total_seconds())*1000)
                #print "query: " + str(int((query_time-insert_time).total_seconds()*1000))
                #print "remove: " + str(int((remove_time-query_time).total_seconds()*1000))
            save_file(KP_LOG)
       

    def experiment_insert_remove_fixed(self):
        self.remove_all_triples()
        clear_file(SIB_LOG)
        clear_file(KP_LOG)
        ranges = [1000] + range(0, 35001, 5000)[1:]
        #ranges = range(20000, 35001, 5000)
        for i in ranges:
            print("Working with " + str(i) + " triples")
            write_file(SIB_LOG, "Working with " + str(i) + " triples\n")
            write_file(KP_LOG, "Working with " + str(i) + " triples\n")
            for j in range(50):
                print("iteration " + str(j))
                start_time = datetime.now()
                subject = self.insert_remove_fixed_triples(i, False)
                insert_time_elapsed = datetime.now()
                self._query_triples(Triple(None, None, None))
                query_time_elapsed = datetime.now()
                self.remove_fixed_triples(subject)
                remove_time_elapsed = datetime.now()
                insert_time = int(round((insert_time_elapsed - start_time).total_seconds()*1000))
                query_time = int(round((query_time_elapsed - insert_time_elapsed).total_seconds()*1000))
                remove_time = int(round((remove_time_elapsed - query_time_elapsed).total_seconds()*1000))
                write_file(KP_LOG, "insert {}\n".format(insert_time))
                write_file(KP_LOG, "query {}\n".format(query_time))
                write_file(KP_LOG, "remove {}\n".format(remove_time))
            save_file(KP_LOG)

    def experiment_db_size(self):
        for i in range(100000):
            self.insert_remove_triples(5000, True)
            log_db_size()
    
kp = KnowledgeProcessor(SIB_IP, SIB_PORT)
kp.join_sib()

kp.experiment_query_example()
#kp.experiment_insert_remove()
#kp.experiment_db_size()
#kp.experiment_insert_remove_fixed()
        
#for i in range(10):
#    kp.insert_remove_triples(10000, False)

#for i in range(100):
#    kp.insert_remove_triples(1)

#kp.remove_all_triples()

kp.leave_sib()
