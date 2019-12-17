FROM python:3.7-stretch

WORKDIR /app
RUN pip install poetry
ADD pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
ADD . /app

CMD python -m cdbot
