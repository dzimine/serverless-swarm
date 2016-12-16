FROM ubuntu:14.04
RUN apt-get update
RUN apt-get install -y -q python-all python-pip 
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt
ADD ./encode /opt/encode/
WORKDIR /opt/encode
ENTRYPOINT ["python", "main.py"]
