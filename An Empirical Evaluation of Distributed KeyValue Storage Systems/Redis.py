import random
import string
from datetime import datetime as dt
import statistics

import redis
from rediscluster import RedisCluster

NUM_OPS = 100000

def run_exp_throughput(myRedis, pairs):
    num = len(pairs)

    start = dt.now()
    for i in range(0, 100):
        print("Running insert: " + str(i) + "% \r")
        j = 0
        while j < (num / 100):
            val = pairs[i * (num // 100)][10:]
            key = pairs[i * (num // 100) + j][:10]
            ## set key-value in redis
            myRedis.set(key,val)       
            j += 1

    for i in range(0, 100):
        print("Running get, and delete: " + str(i) + "% \r")
        j = 0
        while j < (num / 100):
            key = pairs[i * (num // 100) + j][:10]
            myRedis.get(key)
            myRedis.delete(key)
            j += 1
    end = dt.now()

    delta = end - start
    delta_sec = delta.seconds + delta.microseconds / 1000000
    print("Clapsed time! " + str(delta_sec) + " seconds")
    print("Total Throughput " + str(3 * NUM_OPS / delta_sec) + " OPs/s")
    tp = 3 * NUM_OPS / delta_sec
    return tp


def run_exp_latency(myRedis, pairs):
    num = len(pairs)
    delta = []
    for i in range(0, 100):
        print("Running insert, get, and delete: " + str(i) + "% \r")
        j = 0
        while j < (num / 100):
            val = pairs[i * (num // 100)][10:]
            key = pairs[i * (num // 100) + j][:10]                        
            start_in = dt.now()
            myRedis.set(key,val)
            end_in = dt.now()
            delta_in = end_in - start_in

            start_get = dt.now()
            myRedis.get(key)
            end_get = dt.now()
            delta_get = end_get - start_get

            start_det = dt.now()
            myRedis.delete(key)
            end_det = dt.now()
            delta_det = end_det - start_det
            
            delta.append(float(delta_in.microseconds * 0.001))
            delta.append(float(delta_get.microseconds * 0.001))
            delta.append(float(delta_det.microseconds * 0.001))
            j += 1
    print("Total Latency " + str(statistics.mean(delta)) + " ms")
    la = statistics.mean(delta)
    return la


def generate_pair(size, alphabet):
    res = ''
    for _ in range(0, size):
        res += random.choice(alphabet)
    return res


def run_exp_init(num):
    pairs = []
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    for i in range(0, 100):
        j = 0
        while j < (num / 100):
            pair = generate_pair(100, alphabet)
            if pair not in pairs:
                pairs.append(pair)
                j += 1

    print("Initializing random key-value pairs: " + "100% " + "...completed.")
    return pairs


def main():

    # startup_nodes = [{"host": "10.150.87.4", "port": "6379"},
    #                 {"host": "10.150.87.49", "port": "6379"},
    #                 {"host": "10.150.87.66", "port": "6379"},    
    #                 {"host": "10.150.87.85", "port": "6379"},
    #                 {"host": "10.150.87.26", "port": "6379"},
    #                 {"host": "10.150.87.147", "port": "6379"},
    #                 {"host": "10.150.87.109", "port": "6379"},
    #                 {"host": "10.150.87.172", "port": "6379"},
    #                 ]

    startup_nodes = [{"host": "127.0.0.1", "port": "6379"}]
    myRedis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

    # myRedis = redis.Redis(host='127.0.0.1', port=6379, db=0)

    pairs = run_exp_init(NUM_OPS)
    tp = run_exp_throughput(myRedis, pairs)
    la = run_exp_latency(myRedis, pairs)
    print("Total Throughput  " + str(tp) + " OPs/s")
    print("Total Latency " + str(la) + " ms")

if __name__ == "__main__":
    main()
