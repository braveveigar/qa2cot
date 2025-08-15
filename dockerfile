FROM ubuntu:22.04

# RUN rm /bin/sh && ln -s /bin/bash /bin

ENV PYTHON_VERSION=3.10

RUN apt-get update && \
    apt-get install -y python${PYTHON_VERSION} && \
    apt-get install -y python3-pip && \
    apt-get clean

WORKDIR /app

RUN \
    echo 'alias python="/usr/bin/python3"' >> /root/.bashrc && \
    echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc && \
    source /root/.bashrc

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

CMD ["python3", "server.py"]