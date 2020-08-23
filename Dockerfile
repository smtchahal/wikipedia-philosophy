FROM python:3.8-alpine

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY . .

ENTRYPOINT ["./example.py"]
