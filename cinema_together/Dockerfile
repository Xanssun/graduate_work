FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh

RUN  pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY src/. .

EXPOSE 8005

ENTRYPOINT ["sh", "entrypoint.sh"]
