FROM python:3.9-buster
WORKDIR /work

#poetryファイルを取ってきて、dockerのコンテナ上においておく
COPY requirements.txt ./

RUN apt-get update && apt-get install -y tzdata libgdal-dev
RUN pip install --upgrade pip

RUN pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"