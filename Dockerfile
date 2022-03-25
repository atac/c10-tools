FROM python:3.9
COPY . /c10-tools
WORKDIR /c10-tools
RUN python -m pip install -U pip pdm
RUN pip install .
