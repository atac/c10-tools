FROM python:3.7
COPY . /c10-tools
WORKDIR c10-tools
RUN pip3 install -r requirements.txt
RUN pip3 install .
