FROM python:3

RUN apk add --update tini

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
