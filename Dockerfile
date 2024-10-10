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

# Install required packages for Microsoft Edge and msedgedriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    unzip \
    && apt-get clean

# Add Microsoft Edge GPG key and repository
RUN wget -qO - https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/debian/ bookworm main" > /etc/apt/sources.list.d/microsoft-edge.list

# Update package lists and install Microsoft Edge
RUN apt-get update && apt-get install -y microsoft-edge-stable

# Download the appropriate version of msedgedriver
RUN wget -q https://msedgedriver.azureedge.net/LATEST_STABLE/LATEST -O msedgedriver_version \
    && MSEdgeDriver_VERSION=$(cat msedgedriver_version) \
    && wget -q https://msedgedriver.azureedge.net/$MSEdgeDriver_VERSION/msedgedriver_linux64.zip \
    && unzip msedgedriver_linux64.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/msedgedriver \
    && rm msedgedriver_version msedgedriver_linux64.zip

# Copy application files
COPY . $APP_DIR/

# Install Python dependencies
RUN pip install -r requirements.txt

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Command to start our application
CMD python $APP_DIR/app/tgram_bot_runner.py
