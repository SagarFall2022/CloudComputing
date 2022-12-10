### CS553 Cloud Computing Homework 7 Repo
**Illinois Institute of Technology**  

 
**Students**:  
* Sagar Shekhargouda Patil - spatil59@hawk.iit.edu 
* Isa Muradli -imuradli@hawk.iit.edu 
 


1. Setup Apache Cassandra
  # download and install cassandra
    sudo apt update
    
    sudo apt install openjdk-8-jdk
    
    sudo apt install apt-transport-https

    wget -q -O - https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add -
    
    sudo sh -c 'echo "deb http://www.apache.org/dist/cassandra/debian 311x main" > /etc/apt/sources.list.d/cassandra.list'

    sudo apt update

    sudo apt install cassandra

    nodetool status

  # repeat these steps on each of the nodes

  # setup multi node cluster
    sudo service cassandra stop

    sudo rm -rf /var/lib/cassandra/*

    # update cassandra.yaml (/etc/cassandra/cassandra.yaml)
      cluster_name: 'MyCassandraCluster'
      num_tokens: 256
      seed_provider:
        - class_name: org.apache.cassandra.locator.SimpleSeedProvider
          parameters:
        - seeds: "<IP address of node 1 >"
      listen_address: <IP address of container>
      rpc_address: <IP address of container>
      endpoint_snitch: GossipingPropertyFileSnitch
    
    sudo service cassandra start

    nodetool status

  # repeat these steps on each of the VMs

  # run python code

    # download
      sudo apt install pssh
    
      sudo apt-get -y install python3-pip
      
      pip3 install cassandra-driver

      pip3 install scales
    
    # repeat on each nodes


    # running on a single node

      # setup Keyspace and create table
        python3 cassandra_script.py True insert >> node1.log

      # run insert operation
        time python3 cassandra_script.py False insert >> node1.log

      # run lookup operation
        time python3 cassandra_script.py False lookup >> node1.log

      # run remove operation
        time python3 cassandra_script.py False remove >> node1.log

    # running on multiple nodes

      # connect to node 1

      # create nodes.txt - It contains the IP address of each VM nodes for pssh

      # setup Keyspace and create table
        parallel-ssh -A -i -h nodes.txt -- python3 cassandra_script.py True insert >> node1.log

      # run insert operation
        time parallel-ssh -A -i -h nodes.txt -- python3 cassandra_script.py False insert >> node1.log

      # run lookup operation
        time parallel-ssh -A -i -h nodes.txt -- python3 cassandra_script.py False lookup >> node1.log

      # run remove operation
        time parallel-ssh -A -i -h nodes.txt -- python3 cassandra_script.py False remove >> node1.log


2. Setup MongoDB
  
  # mongo db setup  
    
    sudo apt update && sudo apt upgrade

    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add - && sudo apt-get install gnupg
    
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
    
    sudo apt-get update && sudo apt-get install -y mongodb-org
    
    echo "mongodb-org hold" | sudo dpkg --set-selections && echo "mongodb-org-server hold" | sudo dpkg --set-selections
    
    echo "mongodb-org-shell hold" | sudo dpkg --set-selections && echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
    
    echo "mongodb-org-tools hold" | sudo dpkg --set-selections && ps --no-headers -o comm 1
    
    sudo systemctl start mongod && sudo systemctl status mongod

    # setup mongo db authentication
        mongo
        use admin
        db.createUser({user: "mongo-admin", pwd: "password", roles:[{role: "root", db: "admin"}]})
        exit
    # end of mongo db authentication

  # end of mongo db setup

  # setup /etc/hosts file
      sudo vim /etc/hosts
      10.150.87.26 node1 # config server
      10.150.87.147 node2 # query server
      10.150.87.4 node3 # sharding server
       10.150.87.49 node4 # sharding server
      10.150.87.66 node5 # sharding server
       10.150.87.85 node6 # sharding server
   

  # add more servers


  # generate key file

      # perform only on config server
          openssl rand -base64 756 > mongo-keyfile

      # perform on other servers then config server
          sudo vim mongo-keyfile

      #perform on all servers
          cd /opt && sudo mkdir mongo && cd && sudo mv ~/mongo-keyfile /opt/mongo
          sudo chmod 400 /opt/mongo/mongo-keyfile && sudo chown mongodb:mongodb /opt/mongo/mongo-keyfile
          #sudo cat /opt/mongo/mongo-keyfile

          # add following rule
          sudo nano /etc/mongod.conf
          security:
            keyFile: /opt/mongo/mongo-keyfile

          sudo systemctl restart mongod

  # initialize config server
      sudo vim /etc/mongod.conf
      port: 27017
      #bindIp: <ip of config server>
      bindIp: 10.150.87.26

      #uncomment replication section
      replication:
        replSetName: configReplSet

      #uncomment sharding section
      sharding:
        clusterRole: "configsvr"

      sudo systemctl restart mongod
      mongo node1:27019 -u mongo-admin -p --authenticationDatabase admin

      rs.initiate( { _id: "configReplSet", configsvr: true, members: [ { _id: 0, host: "node1:27019" }] } )

      #output should be
      { "ok" : 1 }

      rs.status()
      #output should be

  # initialize query server
      # create /etc/mongos.conf file and copy content as following
      # where to write logging data.
      # where to write logging data.
      systemLog:
        destination: file
        logAppend: true
        path: /var/log/mongodb/mongos.log

      # network interfaces
      net:
        port: 27017
        bindIp: 10.150.87.147

      security:
        keyFile: /opt/mongo/mongo-keyfile

      sharding:
        configDB: configReplSet/node1:27017

      # create /lib/systemd/system/mongos.service file and copy content as following
      [Unit]
      Description=Mongo Cluster Router
      After=network.target

      [Service]
      User=mongodb
      Group=mongodb
      ExecStart=/usr/bin/mongos --config /etc/mongos.conf
      # file size
      LimitFSIZE=infinity
      # cpu time
      LimitCPU=infinity
      # virtual memory size
      LimitAS=infinity
      # open files
      LimitNOFILE=64000
      # processes/threads
      LimitNPROC=64000
      # total threads (user+kernel)
      TasksMax=infinity
      TasksAccounting=false

      [Install]
      WantedBy=multi-user.target

      # The mongos service needs to obtain data locks that conflicts with mongod, so be sure mongod is stopped before proceeding:
      sudo systemctl stop mongod

      # Enable mongos.service so that it automatically starts on reboot, and then initialize the mongos:
      sudo systemctl enable mongos.service
      sudo systemctl start mongos

      systemctl status mongos

      You should see output similar to this:

      # Loaded: loaded (/lib/systemd/system/mongos.service; enabled; vendor preset: enabled)
      # Active: active (running) since Tue 2017-01-31 19:43:05 UTC; 10s ago
      # Main PID: 3901 (mongos)
      # CGroup: /system.slice/mongos.service
      #     └─3901 /usr/bin/mongos --config /etc/mongos.conf

  # Sharded server setup
      sudo vim /etc/mongod.conf
      # Change ip as following:
      bindIp: 10.150.87.4
      # uncomment following
      sharding:
        clusterRole: shardsvr

      sudo systemctl stop mongod && sudo systemctl start mongod && sudo systemctl status mongod

  # Add sharded server to the cluster
      mongo node2:27017 -u mongo-admin -p --authenticationDatabase admin

      # do for the rest of the nodes also
      sh.addShard( "node3:27017" )

  # configure sharding
      mongo node2:27017 -u mongo-admin -p --authenticationDatabase admin

      use exampleDB
      sh.enableSharding("exampleDB")
      use config
      db.databases.find()

  # To enable sharding on the database and collection level
      use exampleDB
      sh.enableSharding("exampleDB")
      db.exampleCollection.ensureIndex( { _id : "hashed" } )
      sh.shardCollection( "exampleDB.exampleCollection", { "_id" : "hashed" } )
      db.exampleCollection.getShardDistribution()

  # steps to execute the code
    # downloads and installs
      sudo apt install python3.8

      sudo apt update
    
      sudo apt install python3-pip

      pip install pymongo

    #run code as following

      python3 Mongo.py
      
      
      
 3. Redis
 
	pip3 install redis
	pip3 install redis-py-cluster
	pip3 install statistics
	
	
	

# 1. Start/restart redis-server on 1/2/4/8 nodes
bash script/node-redis-server-start.sh 4

# 2.1 Validate the cluster is up by
redis-cli -h 10.150.87.26 -c -p 7000

-----------------------------------------------------------------


# Install ruby and redis with
sudo apt-get update
sudo apt install ruby
sudo apt install redis-server


# start redis nodes on machines
redis-server ./redis.conf



# connect to the cluster with cli
redis-cli -h 10.150.87.26 -c -p 7000


#run install-redis.sh to install redis and redis cluster in python
pip3 install redis
pip3 install redis-py-cluster


