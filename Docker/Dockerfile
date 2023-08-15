FROM python:3.10.6

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

CMD ["flask", "run", "--host", "0.0.0.0"]
