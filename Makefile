.PHONY: server frontend install build install-backend install-frontend

PSQL=docker-compose exec -T postgres psql
PGDATABASE=president
PGUSER=president
PGHOST=localhost

server:
	PGUSER=$(PGUSER) PGDATABASE=$(PGDATABASE) PGHOST=$(PGHOST) python app.py

console:
	PGUSER=$(PGUSER) PGDATABASE=$(PGDATABASE) PGHOST=$(PGHOST) python

frontend:
	cd frontend && REACT_APP_SERVER_URL="http://localhost:5000" npm start

install: install-backend install-frontend

install-backend:
	pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

build:
	cd frontend && npm run build

createdb:
	$(PSQL) postgres -U postgres -c "DROP ROLE IF EXISTS $(PGDATABASE); CREATE ROLE $(PGDATABASE) WITH LOGIN CREATEDB;"
	$(PSQL) postgres -U $(PGDATABASE) -c "CREATE DATABASE $(PGDATABASE);"

dropdb:
	$(PSQL) -U postgres postgres -c "DROP DATABASE IF EXISTS $(PGDATABASE);"

recreatedb: dropdb createdb
