FROM tensorflow/tensorflow
RUN pip install --upgrade pip
WORKDIR /logs
ENTRYPOINT ["tensorboard", "--logdir", "/logs", "--host", "0.0.0.0"]   