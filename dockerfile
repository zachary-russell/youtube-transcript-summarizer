FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y gcc && \
    pip install --no-cache-dir -r requirements.txt

COPY data/stopwords/stopwords data/stopwords/stopwords

COPY . .

CMD ["python", "app.py"]

