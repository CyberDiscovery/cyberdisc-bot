FROM python:3.7-alpine3.9

RUN apk add build-base freetype-dev git jpeg-dev libffi-dev zlib-dev

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app

CMD python -m cdbot
