FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 

RUN pip install Pyrebase4

COPY requirements.txt .
RUN pip install -r requirements.txt
