FROM python:3.10.10-slim-bullseye

ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install poetry==1.4.0
RUN poetry config virtualenvs.create false
RUN poetry export -f requirements.txt --with dev --output ./requirements.txt
RUN python -m pip install -r ./requirements.txt
