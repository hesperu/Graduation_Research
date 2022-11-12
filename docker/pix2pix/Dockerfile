#ここからnvidia/cudaのための設定
#公式の設定を参照している。https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/11.8.0/ubuntu1804/runtime/cudnn8/Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu18.04 as base

FROM base as base-amd64

ENV NV_CUDNN_VERSION 8.6.0.163
ENV NV_CUDNN_PACKAGE_NAME "libcudnn8"

ENV NV_CUDNN_PACKAGE "libcudnn8=$NV_CUDNN_VERSION-1+cuda11.8"

FROM base-${TARGETARCH}

ARG TARGETARCH

LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"
LABEL com.nvidia.cudnn.version="${NV_CUDNN_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ${NV_CUDNN_PACKAGE} \
    && apt-mark hold ${NV_CUDNN_PACKAGE_NAME} \
    && rm -rf /var/lib/apt/lists/*

#ここまで
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install vim wget curl

RUN pip install torch tqdm numpy matplotlib jupyter pandas imageio 