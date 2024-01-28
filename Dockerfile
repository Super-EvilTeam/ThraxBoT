# Use the official Python image as a base
FROM python:3.11.4

# Set the working directory to /app
WORKDIR /app

# Copy your project files to the container
COPY . /app

# Install the necessary dependencies
RUN pip install virtualenv

# Create the virtual environment and install dependencies
RUN python setup_script.py

# Command to run the main script
CMD ["python", "main.py"]
