# Run tests inside a container
FROM ubuntu:latest
MAINTAINER GNS3 Team

RUN apt-get update
RUN apt-get install -y --force-yes python3 python3-pyqt6 python3-pip python3-pyqt6.qtsvg python3-pyqt6.qtwebsockets python3-dev xvfb
RUN apt-get clean

ADD dev-requirements.txt /dev-requirements.txt
ADD requirements.txt /requirements.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir -r /dev-requirements.txt

ADD . /src
WORKDIR /src

CMD xvfb-run python3 -m pytest -vv
