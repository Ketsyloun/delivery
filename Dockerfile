FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install poetry==1.1.13

ENV PATH="/root/.local/bin:$PATH"

RUN poetry --version

COPY pyproject.toml poetry.lock /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.9

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

ENV PYTHONPATH=/code/src:$PYTHONPATH

CMD ["uvicorn", "src.delivery.main:app", "--host", "0.0.0.0", "--port", "80"]
