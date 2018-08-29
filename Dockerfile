FROM python:3.6-alpine3.7

RUN apk add --update --no-cache tini
RUN apk add --update --no-cache build-base
RUN apk add --update --no-cache libffi-dev
RUN apk --update --no-cache add imagemagick

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
