# vim: set ft=dockerfile:

FROM usgsastro/ubuntu:latest

SHELL ["/bin/bash", "-lc"]

RUN apt-get update &&       \
    apt-get install -y      \
        curl                \
        gcc                 \
        g++                 \
        git                 \
        libgl1-mesa-dev     \
    &&                      \
    rm -rf /var/cache/apt/*

RUN curl -sLo /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&    \
    chmod +x /tmp/miniconda.sh &&                                                                           \
    /tmp/miniconda.sh -b -p /opt/conda &&                                                                   \
    rm /tmp/miniconda.sh &&                                                                                 \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh &&                                      \
    echo '. /opt/conda/etc/profile.d/conda.sh' >> /etc/bash.bashrc

RUN git config --system http.sslCAInfo /etc/ssl/certs/ca-certificates.crt &&        \ 
    echo 'ssl_verify: /etc/ssl/certs/ca-certificates.crt' > /opt/conda/.condarc &&  \
    echo 'always_yes: true' >> /opt/conda/.condarc &&                               \
    conda update conda

RUN useradd -m conda
USER conda
WORKDIR /home/conda
# rootじゃ無いと出来ない処理をやっておく
USER root
COPY init.sh /home/conda/init.sh
RUN chmod 777 /home/conda/init.sh
RUN mkdir /home/data
USER conda


#自分が追加したやつ。この設定のままだと色々不便だから。
CMD ["/bin/bash","/home/conda/init.sh"]