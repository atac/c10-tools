FROM python:3.7

COPY . /c10-tools
WORKDIR c10-tools
RUN apt update && apt install -y python3-dev
RUN python3 -m pip install -U pip
RUN pip3 install -r requirements.txt

RUN python3 setup.py link
WORKDIR /
RUN export PATH=/c10-tools/src:$PATH
