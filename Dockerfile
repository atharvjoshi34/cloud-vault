# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 8080 for the Flask app to run on
EXPOSE 8080

# Define environment variable for Flask to run in production mode
ENV FLASK_ENV=production

# Run the Flask app
CMD ["python", "app.py"]
