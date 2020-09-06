FROM tensorflow/tensorflow:2.3.0rc0-gpu-jupyter

ADD ./requirements.txt .

RUN apt-get update -y && apt-get install git wget vim libsm6 libxext6 libxrender-dev libx264-dev ffmpeg tesseract-ocr libtesseract-dev openjdk-11-jdk-headless maven -y
RUN pip install -r requirements.txt

EXPOSE 8888
