FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN apt update \
#    && apt add postgresql-dev gcc python3-dev musl-dev





RUN pip install cchardet





RUN apt-get install libffi-dev






COPY requirements.txt ./
RUN pip install -r requirements.txt



COPY . .


ENTRYPOINT ["./entrypoint.sh"]

