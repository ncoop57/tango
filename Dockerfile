FROM tensorflow/tensorflow:2.3.0rc0-gpu-jupyter

#ADD ./requirements.txt .

#RUN pip install -r requirements.txt
#RUN apt-get update -y && apt-get install git wget vim libsm6 libxext6 libxrender-dev libx264-dev tesseract-ocr libtesseract-dev -y

EXPOSE 8888 6006
