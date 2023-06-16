# Use the Python 3.8 slim image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install gsutil
RUN apt-get update && apt-get install -y curl gnupg
RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y google-cloud-sdk

# Download model from gcs
RUN mkdir -p ./models
RUN gsutil -m cp -r gs://github_demo_bucket/opus-mt-en-de ./models/

# Copy the requirements file to the container
COPY . .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
