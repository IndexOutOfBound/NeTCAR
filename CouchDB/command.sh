




docker service create --name couchdb-master -p 8091:8091 --replicas 1 --network couchdb -e TYPE=MASTER arungupta/couchdb:swarm


docker service create --name couchdb-worker --replicas 1 -e TYPE=WORKER -e COUCHBASE_MASTER=couchdb-master.couchdb --network couchdb arungupta/couchdb:swarm
