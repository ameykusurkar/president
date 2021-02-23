.PHONY: server frontend

server:
	python app.py

frontend:
	cd frontend && npm start
