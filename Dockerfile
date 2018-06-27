FROM python:3.6-alpine3.7

RUN apk add --update tini

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
