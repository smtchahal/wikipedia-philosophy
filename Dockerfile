FROM python:3.13-alpine AS base

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY . .

FROM base AS test

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

ENTRYPOINT ["pytest", "--cov=philosophy", "--cov-report=term-missing"]

FROM base AS app

ENTRYPOINT ["./example.py"]
