FROM python:3.9.1
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
COPY serialize.py .
COPY game/* game/
EXPOSE 5000
CMD ["python", "app.py"]
