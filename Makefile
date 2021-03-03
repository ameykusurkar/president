.PHONY: server frontend install

server:
	python app.py

frontend:
	cd frontend && REACT_APP_SERVER_URL="http://localhost:5000" npm start

install:
	pip install -r requirements.txt
	cd frontend && npm install
