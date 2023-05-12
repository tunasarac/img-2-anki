# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10

# Copy local code to the container image.
WORKDIR /app
COPY . .


#Install tesseract
RUN apt-get update -qqy && apt-get install -qqy \
        tesseract-ocr \
        libtesseract-dev \
        tesseract-ocr-deu

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download de_core_news_md

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
ENTRYPOINT ["python", "app.py"]