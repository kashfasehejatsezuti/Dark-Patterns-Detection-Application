# Base python image
FROM python:3.11.5

# Setting working directory as /app inside docker container
WORKDIR /app

# Copy the requirements file to /app
COPY requirements.txt .

# Install requried dependencies inside the container
RUN pip install -r requirements.txt

# Copy the remaining code from local machine to /app inside container
COPY . .

# Set the environment variable to disable Python output buffering
ENV PYTHONUNBUFFERED=1

# Run the ml model service
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:5001", "-w", "4", "--timeout", "120"]
