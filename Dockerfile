# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the Gunicorn port
EXPOSE 8010


ENV DJANGO_DEBUG=False
ENV DB_NAME=
ENV DB_HOST=
ENV DB_USER=postgres
ENV DB_PASSWORD=


CMD python manage.py migrate && gunicorn --config conf/gunicorn.conf.py core.wsgi --preload
