# Use official Python image
FROM python:3.10-slim

# Install sqlite and dependencies
RUN apt update && \
    apt install -y libsqlcipher-dev gcc && \
    pip install --upgrade pip

# Set workdir to project root
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy all project files
COPY . .

# Ensure uploads directory exists
RUN mkdir -p uploads

# Expose port
EXPOSE 5032

# Initialize DB and run app
CMD ["python3", "app.py"]

