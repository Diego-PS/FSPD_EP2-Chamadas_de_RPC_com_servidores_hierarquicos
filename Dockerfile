FROM ubuntu:22.04

RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install grpcio
RUN pip3 install grpcio-tools

WORKDIR /work