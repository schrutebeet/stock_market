# Use an official Python runtime as a parent image
FROM python:3.11.6

# Set the shell to exit immediately if a command exits with a non-zero status
RUN set -e

# Set the working directory to /app
WORKDIR /stocksapp

# Create logs directory 
RUN mkdir /logs

# Define environment variable
ENV LOGS_PATH /logs

# Copy the current directory contents into the container at /stocksapp
COPY . /stocksapp

# Install any needed packages specified in requirements.txt
RUN pip install -r /stocksapp/dependencies/requirements.txt

# Run app.py when the container launches
CMD ["python", "-m", "src.main"]
