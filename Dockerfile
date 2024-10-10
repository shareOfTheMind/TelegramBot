# Use the specified Python version
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_DIR=/srv/telegram_service
ENV VENV_DIR=$APP_DIR/api_service_venv
ENV LOG_DIR=$APP_DIR/logs
ENV CONFIG_DIR=$APP_DIR/app/config
ENV LOG_FILE=$LOG_DIR/docker_build_deploy.log

# Set working directory
WORKDIR $APP_DIR

# Create the logs directory
RUN mkdir -p $LOG_DIR

# Create a function for logging
RUN echo '#!/bin/bash' > /usr/local/bin/log && \
    echo 'log() {' >> /usr/local/bin/log && \
    echo '    local msg="$1";' >> /usr/local/bin/log && \
    echo '    local timestamp="$(date +\"%Y-%m-%d %H:%M:%S\")";' >> /usr/local/bin/log && \
    echo '    echo "$timestamp - $msg" >> "/srv/telegram_service/logs/docker_build_deploy.log";' >> /usr/local/bin/log && \
    echo '}' >> /usr/local/bin/log && \
    chmod +x /usr/local/bin/log


# Create deploy log file and initialize log
RUN touch "$LOG_FILE" && \
    /usr/local/bin/log "Starting the build process"

# Install required packages for downloading and installing Microsoft Edge
RUN /usr/local/bin/log "Installing Dependencies" && \
    apt-get update && \
    apt-get install -y gpg wget gnupg apt-transport-https unzip && \
    apt-get clean && \
    /usr/local/bin/log "Dependencies installed successfully" || /usr/local/bin/log "Failed to install dependencies"

# Add the Microsoft GPG key and run installation/add repo; Install Microsoft Edge
RUN /usr/local/bin/log "Installing Microsoft Edge" && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge-dev.list && \
    apt-get update && \
    apt-get -y install microsoft-edge-stable && \
    /usr/local/bin/log "Microsoft Edge installed successfully" || /usr/local/bin/log "Failed to install Microsoft Edge"

# Download the specific version of msedgedriver
RUN /usr/local/bin/log "Installing Edge WebDriver" && \
    wget -q https://msedgedriver.azureedge.net/129.0.2792.86/edgedriver_linux64.zip -O /tmp/edgedriver_linux64.zip && \
    unzip /tmp/edgedriver_linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/msedgedriver && \
    rm /tmp/edgedriver_linux64.zip && \
    /usr/local/bin/log "Edge WebDriver installed successfully" || /usr/local/bin/log "Failed to install Edge WebDriver"

# Log before copying application files
RUN /usr/local/bin/log "Generating Application Files"

# Copy application files
COPY . $APP_DIR/

# Log before installing Python packages
RUN /usr/local/bin/log "Installing Python Packages" && \
    pip install -r requirements.txt && \
    pip install debugpy && \
    /usr/local/bin/log "Python packages installed successfully" || /usr/local/bin/log "Failed to install Python packages"

# Log mapping volumes
RUN /usr/local/bin/log "Mapping Volumes"

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Log running the application
RUN /usr/local/bin/log "Running the Application"

# Command to start the application
CMD ["python", "/srv/telegram_service/app/tgram_bot_runner.py"]