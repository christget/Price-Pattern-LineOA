FROM tiangolo/uvicorn-gunicorn:python3.11-slim
RUN mkdir /yolov8-fastapi-test
COPY ./requirements.txt /yolov8-fastapi-test/requirements.txt
RUN apt-get update
RUN apt-get install gcc ffmpeg libsm6 libxext6 openssh-client -y
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir --upgrade -r /yolov8-fastapi-test/requirements.txt || cat /yolov8-fastapi-test/requirements.txt
COPY . /yolov8-fastapi-test
WORKDIR /yolov8-fastapi-test
CMD uvicorn main:app  --host=0.0.0.0 --port=${PORT:-8000}