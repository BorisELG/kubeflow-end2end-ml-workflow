FROM python:3.7-slim

RUN pip install --upgrade pip && pip install kfserving numpy pillow
WORKDIR /app
COPY mytransformer.py /app

ENTRYPOINT ["python", "mytransformer.py"]
