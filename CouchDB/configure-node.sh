
#!/bin/bash

set -x
set -m



sleep 15

echo \"-setcookie couchdb_cluster\" >> /opt/couchdb/etc/vm.args 

echo \"-name couchdb@${nodes}\" >> /opt/couchdb/etc/vm.args


export masternode=172.26.37.183

export node=`hostname -I | cut -f1 -d' '`
export user=admin
export pass=admin

docker run --name couchdb-master -p 5984:5984 -d couchdb:2.3.0


declare cont=(`docker ps --all | grep couchdb | cut -f1 -d' '`)

docker exec ${cont} \
      bash -c "echo \"-setcookie couchdb_cluster\" >> /opt/couchdb/etc/vm.args"

docker exec ${cont} \
      bash -c "echo \"-name couchdb@${node}\" >> /opt/couchdb/etc/vm.args"

docker exec ${cont} \
      bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"

docker exec ${cont} \
      bash -c "echo \"-kernel inet_dist_listen_max 9100\" >> /opt/couchdb/etc/vm.args"



docker restart ${cont}


erl -name car@172.26.37.182 -setcookie 'brumbrum' -kernel inet_dist_listen_min 9100 -kernel inet_dist_listen_max 9200

erl -name bus@172.26.37.183 -setcookie 'brumbrum' -kernel inet_dist_listen_min 9100 -kernel inet_dist_listen_max 9200

curl -XPUT "http://${node}:5984/_node/_local/_config/admins/${user}" --data "\"${pass}\""

curl -XPUT "http://${user}:${pass}@${node}:5984/_node/couchdb@${node}/_config/chttpd/bind_address" --data '"0.0.0.0"'


# curl -X POST -H "Content-Type: application/json" http://${user}:${pass}@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"admin", "node_count":"2"}'


curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
        \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
        \"remote_node\": \"${node}\", \
        \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"


curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"add_node\", \"host\":\"${node}\", \
        \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"


curl -X GET "http://${user}:${pass}@${node}:5984/_membership"






curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}" 

rev=`curl -XGET "http://${masternode}:5986/_nodes/nonode@nohost" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://${masternode}:5986/_nodes/nonode@nohost?rev=${rev}"  --user "${user}:${pass}"






curl -X POST -H "Content-Type: application/json" \
 http://${user}:${pass}@${node}:5984/_cluster_setup \
  -d '{"action": "enable_cluster", "bind_address":"0.0.0.0","username": "admin", "password":"password", "node_count":"2"}'




curl -X POST -H "Content-Type: application/json" \
http://${user}:${pass}@${masternode}:5984/_cluster_setup \
-d '{"action": "enable_cluster", "bind_address":"0.0.0.0","username": "admin", "password":"password", "port": 5984, "node_count": "3", "remote_node": "<remote-node-ip>", "remote_current_user": "<remote-node-username>", "remote_current_password": "<remote-node-password>" }'

curl -X POST -H "Content-Type: application/json" \
http://${user}:${pass}@${masternode}:5984/_cluster_setup \
-d '{"action": "add_node", "host":"<remote-node-ip>", "port": <remote-node-port>, "username": "admin", "password":"pass"}'



















echo "Type: $TYPE"





if [ "$TYPE" = "WORKER" ]; then
  echo "Sleeping ..."
  sleep 15

  #IP=`hostname -s`
  IP=`hostname -I | cut -d ' ' -f1`
  echo "IP: " $IP

  echo "Auto Rebalance: $AUTO_REBALANCE"
  if [ "$AUTO_REBALANCE" = "true" ]; then
    couchbase-cli rebalance --cluster=$COUCHBASE_MASTER:8091 --user=Admin --password=password --server-add=$IP --server-add-username=Admin --server-add-password=password
  else
    couchbase-cli server-add --cluster=$COUCHBASE_MASTER:8091 --user=Admin --password=password --server-add=$IP --server-add-username=Admin --server-add-password=password
  fi;
fi;

fg 1