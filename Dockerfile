FROM python:3
USER root

RUN pip install --upgrade pip
RUN python -m pip install numpy
RUN python -m pip install discord.py
RUN python -m pip install pyyaml
RUN python -m pip install mysqlclient
