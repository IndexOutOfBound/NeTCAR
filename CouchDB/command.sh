




docker service create --name couchbase-master -p 8091:8091 --replicas 1 --network couchbase -e TYPE=MASTER arungupta/couchbase:swarm


docker service create --name couchbase-worker --replicas 1 -e TYPE=WORKER -e COUCHBASE_MASTER=couchbase-master.couchbase --network couchbase arungupta/couchbase:swarm
