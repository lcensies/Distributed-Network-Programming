
nodes=()

echo "LUL"

for i in {1..3}; do
  
  node_pid=$(bash -c "echo $$")
  echo "Started node ${i} with pid ${node_pid}" 
  nodes+=( $node_pid )
done

trap _term SIGTERM

echo "Started servers"

_term() { 
  echo "Caught SIGTERM signal!" 
  for node in "${nodes[@]}"; do
    kill node
  done
}

while ::