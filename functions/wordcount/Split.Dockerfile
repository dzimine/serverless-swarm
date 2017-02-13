FROM python:2.7-alpine

COPY requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt
COPY ./wordcount /opt/wordcount/
WORKDIR /opt/wordcount

ENTRYPOINT ["python", "split.py"]
