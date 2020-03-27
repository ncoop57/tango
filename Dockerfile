FROM tensorflow/tensorflow:2.0.0rc0-gpu-py3-jupyter

ADD ./requirements.txt .

RUN pip install -r requirements.txt
RUN apt-get update -y && apt-get install git wget vim python3-opencv libsm6 libxext6 libxrender-dev -y

EXPOSE 8888
