FROM python:3.10.10-slim-bullseye

ENV PYTHONPATH=.
ENV PYTHONUNBUFFERED=1


COPY /cli /cli
COPY /libs /libs
COPY ./pyproject.toml ./pyproject.toml 

RUN pip install poetry==1.4.0
WORKDIR /cli

RUN poetry config virtualenvs.create false
# No hashes to ensure the local libs module can be installed
RUN poetry export --without-hashes -f requirements.txt --with dev --output ./requirements.txt
RUN python -m pip install -r ./requirements.txt

WORKDIR /