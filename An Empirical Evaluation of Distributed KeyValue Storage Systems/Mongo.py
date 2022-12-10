from pymongo import MongoClient
import random
import string
import time

def randomString(slen=10, num = 10):
    random.seed(1)
    keyValuers = []
    for x in range(num):
        word = string.ascii_lowercase
        keyValuers.append(''.join(random.choice(word) for i in range(slen)))
    return keyValuers

def experiment(num):
    try:
        conn = MongoClient('10.150.87.26',27017)
        print("MongoDB Connected successfully!!")
    except:
        print("Could not connect to MongoDB")

    # database
    db = conn.test
    collection = db.sag1
    word = string.ascii_lowercase

    keys = randomString(10, num)
    valuers = randomString(90, num)

    #Insert Record
    start_time=time.time()
    for i, key in enumerate(keys):
        value = valuers[i]
        key_val = {
                "_id":key,
                "value":valuers[i]
            }
       
        rec_id = collection.insert_one(key_val)
    elapsed_time=time.time()-start_time
    print("Insert Time: ", elapsed_time)

    #Query Record
    start_time = time.time()
    for key in keys:
        rec_id = collection.find({"_id":key})
        
    elapsed_time = time.time()-start_time
    print("Lookup Time: ", elapsed_time)

    #Delete Record
    start_time = time.time()
    for key in keys:
        print(key)
        rec_id = collection.delete_one({"_id":key})

    elapsed_time = time.time()-start_time
    print("Delete Time", elapsed_time)


experiment(10000)
