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

# Create the logs directory
RUN mkdir -p $LOG_DIR

# Create a function for logging
RUN echo '#!/bin/bash\n\
log() { \
    local msg="$1"; \
    local timestamp="$(date +\'%Y-%m-%d %H:%M:%S\')"; \
    echo "$timestamp - $msg" >> "$LOG_FILE"; \
}' > /usr/local/bin/log && chmod +x /usr/local/bin/log

# Create deploy log file and initialize log
RUN LOG_FILE="$LOG_DIR/docker_build_$(date '+%Y-%m-%d_%H-%M-%S').log" && \
    touch "$LOG_FILE" && \
    log "Starting the build process"

# Install required packages for downloading and installing Microsoft Edge
RUN log "Installing Dependencies" && \
    apt-get update && \
    apt-get install -y gpg wget gnupg apt-transport-https unzip && \
    apt-get clean && \
    log "Dependencies installed successfully" || log "Failed to install dependencies"

# Add the Microsoft GPG key and run installation/add repo; Install Microsoft Edge
RUN log "Installing Microsoft Edge" && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge-dev.list && \
    apt-get update && \
    apt-get -y install microsoft-edge-stable && \
    log "Microsoft Edge installed successfully" || log "Failed to install Microsoft Edge"

# Download the specific version of msedgedriver
RUN log "Installing Edge WebDriver" && \
    wget -q https://msedgedriver.azureedge.net/129.0.2792.86/edgedriver_linux64.zip -O /tmp/edgedriver_linux64.zip && \
    unzip /tmp/edgedriver_linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/msedgedriver && \
    rm /tmp/edgedriver_linux64.zip && \
    log "Edge WebDriver installed successfully" || log "Failed to install Edge WebDriver"

# Log before copying application files
RUN log "Generating Application Files"

# Copy application files
COPY . $APP_DIR/

# Log before installing Python packages
RUN log "Installing Python Packages" && \
    pip install -r requirements.txt && \
    pip install debugpy && \
    log "Python packages installed successfully" || log "Failed to install Python packages"

# Log mapping volumes
RUN log "Mapping Volumes"

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Log running the application
RUN log "Running the Application"

# Command to start the application
CMD ["python", "/srv/telegram_service/app/tgram_bot_runner.py"]