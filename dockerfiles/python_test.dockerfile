FROM python:3.10.10-slim-bullseye

ENV PYTHONPATH=/amp/
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install poetry==1.4.0
RUN poetry config virtualenvs.create false
RUN poetry install --with dev --no-root
