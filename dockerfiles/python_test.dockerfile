FROM python:3.10.10-slim-bullseye

ENV PYTHONPATH=/amp/
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install -r ./requirements.txt