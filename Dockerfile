FROM python:3.7-stretch

WORKDIR /app
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
ADD ./pyproject.toml /app/pyproject.toml
ADD ./poetry.lock /app/poetry.lock
RUN poetry install --no-dev
ADD . /app

CMD poetry run cdbot
