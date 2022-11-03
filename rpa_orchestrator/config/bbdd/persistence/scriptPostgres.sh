psql -h localhost -U postgres -f ./databaseAndTables.sql
psql -h localhost -U postgres -f ./inserts.sql
psql -h localhost -U postgres -f ./insertsSettings.sql
psql -h localhost -U postgres -f ./processDatabase.sql