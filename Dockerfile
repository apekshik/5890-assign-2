# Use a lightweight Linux distribution (Alpine) with Python installed as the base image
FROM python:3.8-alpine

# Set the working directory in the container
WORKDIR /app

# Copy your Python application files into the container
COPY . /app

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Expose the port your key-value store will run on
EXPOSE 8888

# Define the command to run your application
CMD ["python", "InMemoryDataStore.py"]
