# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY . /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

COPY requirements.txt /app
RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*
