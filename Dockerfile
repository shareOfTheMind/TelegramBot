# Use the specified Python version
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_DIR=/srv/telegram_service
ENV VENV_DIR=$APP_DIR/api_service_venv
ENV LOG_DIR=$APP_DIR/logs
ENV CONFIG_DIR=$APP_DIR/app/config

# Set working directory
WORKDIR $APP_DIR

# Install necessary packages
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . $APP_DIR/

# Create the virtual environment and install dependencies
RUN python -m venv $VENV_DIR && \
    $VENV_DIR/bin/pip install --upgrade pip && \
    $VENV_DIR/bin/pip install -r requirements.txt

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Command to start our application
CMD ["python", "$APP_DIR/app/tgram_bot_runner.py"]
