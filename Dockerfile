FROM python:3.7-stretch

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app

CMD python -m cdbot
