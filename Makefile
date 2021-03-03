.PHONY: server frontend install build

server:
	python app.py

frontend:
	cd frontend && REACT_APP_SERVER_URL="http://localhost:5000" npm start

install:
	pip install -r requirements.txt
	cd frontend && npm install

build:
	cd frontend && npm run build
