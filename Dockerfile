FROM python:3

RUN apk add --update tini

ADD . /

RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
