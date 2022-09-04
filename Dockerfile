FROM python:3.10-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt



COPY . .


ENTRYPOINT ["./entrypoint.sh"]

