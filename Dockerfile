FROM python:3.6-alpine3.6

RUN apk add --update --no-cache tini
RUN apk add --update --no-cache build-base
RUN apk add --update --no-cache libffi-dev
RUN apk --update --no-cache add imagemagick-dev=6.9.6.8-r1 --repository http://dl-cdn.alpinelinux.org/alpine/v3.5/main/

ADD . /

RUN pip install -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["python", "-m", "bot"]
