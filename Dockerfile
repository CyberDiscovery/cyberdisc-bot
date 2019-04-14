FROM python:3.7-alpine3.9

RUN apk add git build-base libffi-dev zlib-dev jpeg-dev freetype-dev

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install -e git+https://github.com/Rapptz/discord.py@dea3ba5eb7c99f54c72b11f3e3f7b8f41649e779#egg=discord.py
ADD . /app

CMD python -m cdbot
