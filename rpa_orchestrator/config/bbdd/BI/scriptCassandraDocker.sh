docker cp ./GenerateKeyTable.cql cassandra:/
docker exec -it cassandra cqlsh -f ./GenerateKeyTable.cql
