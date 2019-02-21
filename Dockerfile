FROM python:3.7-alpine3.9

RUN apk add --update --no-cache git
RUN apk add --update --no-cache tini
RUN apk add --update --no-cache build-base
RUN apk add --update --no-cache libffi-dev
RUN apk add --update --no-cache zlib-dev
RUN apk add --update --no-cache jpeg-dev

COPY . /app
WORKDIR /app

RUN mkdir -p ~/.config/pypoetry
RUN pip install poetry==1.0.0a2
RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "cdbot"]
