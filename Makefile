.PHONY: server frontend install

server:
	python app.py

frontend:
	cd frontend && npm start

install:
	pip install -r requirements.txt
	cd frontend && npm install
