# Python Docker image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install container dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gettext \
    libpq-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    netcat-openbsd

# Copy all files
COPY . .

# Copy entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies
RUN python3 -m pip install --upgrade setuptools wheel
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set the server port
EXPOSE 8000

# Start up the backend server using the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
