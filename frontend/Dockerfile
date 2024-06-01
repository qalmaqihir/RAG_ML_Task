# Streamlit service
FROM python:3.9 AS base

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend files
COPY frontend.py .

# Command to run Streamlit app
CMD ["streamlit", "run", "frontend.py"]

EXPOSE 8000
