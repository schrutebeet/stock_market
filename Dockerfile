# Use an official Python runtime as a parent image
FROM python:3.11.6

# Set the working directory to /app
WORKDIR /stocksapp

# Copy the current directory contents into the container at /stocksapp
COPY . /stocksapp

# Copy the different chromedrivers into the container at /stocksapp
COPY  /stocksapp

# Install any needed packages specified in requirements.txt
RUN pip install -r /stockapp/dependencies/requirements.txt

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
