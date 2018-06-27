FROM python:3.6-alpine3.7

RUN apk add --update tini
RUN apk add --update build-base
RUN apk add --update libffi-dev

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
