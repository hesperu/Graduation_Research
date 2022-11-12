FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu18.04 as base

RUN apt-get update && apt-get install -y --no-install-recommends
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install vim wget curl
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install torch tqdm numpy matplotlib pandas pillow
