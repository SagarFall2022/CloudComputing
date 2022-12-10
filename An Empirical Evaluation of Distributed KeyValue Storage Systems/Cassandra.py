from cassandra.cluster import Cluster
from cassandra.query import tuple_factory, BatchStatement, ConsistencyLevel, SimpleStatement
from random import seed
from random import random
import time
import random
import string

def randomString(stringLen=10, num = 10):
    random.seed(1)
    keyValRS = []
    for x in range(num):
        lett = string.ascii_lowercase
        keyValRS.append(''.join(random.choice(lett) for i in range(stringLen)))
    return keyValRS

def experiment(num):
    cluster = Cluster(['10.150.87.26'])
    session = cluster.connect('HW7SP')
    keyrs = randomString(10, num)
    valuers = randomString(90, num)
    start_time = time.time()
    insert_user = session.prepare("INSERT INTO maintable (key, value) VALUES (?, ?)")
    for i,key in enumerate(keyrs):
        batchkey = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        batchkey.add(insert_user,(key, valuers[i]))
        session.execute(batchkey)
    elapsed_time = time.time() - start_time
    print("Insert Time: ", elapsed_time)
    start_time = time.time()
    value = ""
    for key in keyrs:
        query = SimpleStatement("SELECT value from maintable where key='{key1}';".format(key1=key), consistency_level=ConsistencyLevel.ONE)
        resultrs = session.execute(query)
    elapsed_time = time.time() - start_time
    print("Look Up Time: ", elapsed_time)

    start_time = time.time()
    for key in keyrs:
        query = SimpleStatement("DELETE FROM maintable WHERE key='{key1}';".format(key1=key), consistency_level=ConsistencyLevel.ONE)
        result = session.execute(query)
    elapsed_time = time.time() - start_time
    print("Delete Time: ", elapsed_time)
    print("Finished expriment", num)

experiment(10000)

