docker network create --driver bridge couch
cp cookie /tmp

docker run -d --name couchdb.one \
 --net=couch \
 -p 5984:5984 \
 -e NODENAME=couchdb.one \
 -e COUCHDB_USER=admin \
 -e COUCHDB_PASSWORD=admin \
 -v /tmp/my.cookie:/opt/couchdb/.erlang.cookie \
couchdb:latest
