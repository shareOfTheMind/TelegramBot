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

# Create deploy log file and initialize log
RUN touch "$LOG_FILE" && \
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Starting the build process" >> "$LOG_FILE"

# Install required packages for downloading and installing Microsoft Edge
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Installing Required Dependencies" >> "$LOG_FILE" && \
    apt-get update && \
    apt-get install -y gpg wget gnupg apt-transport-https unzip && \
    apt-get clean && \
    echo "Dependencies installed successfully" || log "Failed to install dependencies"

# Add the Microsoft GPG key and run installation/add repo; Install Microsoft Edge
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Installing Microsoft Edge" >> "$LOG_FILE" && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge-dev.list && \
    apt-get update && \
    apt-get -y install microsoft-edge-stable && \
    && echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Microsoft Edge installed successfully" >> "$LOG_FILE" || echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - Failed to install Microsoft Edge" >> "$LOG_FILE"

# Download the specific version of msedgedriver
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Installing Edge WebDriver" >> "$LOG_FILE" && \
    wget -q https://msedgedriver.azureedge.net/129.0.2792.86/edgedriver_linux64.zip -O /tmp/edgedriver_linux64.zip && \
    unzip /tmp/edgedriver_linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/msedgedriver && \
    rm /tmp/edgedriver_linux64.zip && \
    && echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Edge WebDriver installed successfully" >> "$LOG_FILE" || echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - Failed to install Edge WebDriver" >> "$LOG_FILE"

# Log before copying application files
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Generating Application Files" >> "$LOG_FILE"

# Copy application files
COPY . $APP_DIR/

# Log before installing Python packages
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Installing Python Packages" >> "$LOG_FILE" && \
    pip install -r requirements.txt && \
    pip install debugpy && \
    && echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Python packages installed successfully" >> "$LOG_FILE" || echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - Failed to install Python packages" >> "$LOG_FILE"

# Log mapping volumes
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Mapping Volumes" >> "$LOG_FILE"

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Log running the application
RUN echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - Starting the Application..." >> "$LOG_FILE"

# Command to start the application
CMD ["python", "/srv/telegram_service/app/tgram_bot_runner.py"]