FROM python:3.11-slim-buster AS build

WORKDIR /build

RUN pip install poetry

RUN python3 -m pip install poetry --no-cache-dir
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml /build/pyproject.toml
COPY poetry.lock /build/poetry.lock

RUN poetry install --no-root --without dev

FROM python:3.11-slim-buster

WORKDIR /ButterflyMX-444

COPY --from=build /build/.venv/ /ButterflyMX-444/.venv/

COPY static /ButterflyMX-444/static
COPY butterflymx_444 /ButterflyMX-444/butterflymx_444

RUN chmod +x /ButterflyMX-444/.venv/bin/uvicorn

CMD [".venv/bin/python3", ".venv/bin/uvicorn", "butterflymx_444:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
