FROM ubuntu:latest

RUN apt-get update && apt-get -y --no-install-recommends install \
build-essential \
clang \
cmake

COPY . ./BTRFdom

WORKDIR /BTRFdom

RUN cmake -DBUILD_SHARED_LIBS=ON .
RUN make

