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

# Create deploy log file
RUN LOG_FILE="$APP_DIR/logs/docker_build_$(date '+%Y-%m-%d').log" \
    touch "$LOG_FILE" && \
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting the build process" >> "$LOG_FILE"

# Install required packages for downloading and installing Microsoft Edge
RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Installing Dependencies" >> "$LOG_FILE" \
    apt-get update && apt-get install -y \
    gpg \
    wget \
    gnupg \
    apt-transport-https \
    unzip \
    && apt-get clean


# Add the Microsoft GPG key and run installation/add repo; Install Microsoft Edge
RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Installing Microsoft Edge" >> "$LOG_FILE" \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge-dev.list \
    && apt-get update \
    && apt-get -y install microsoft-edge-stable


# Download the specific version of msedgedriver
RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Installing Edge WebDriver" >> "$LOG_FILE" \
    wget -q https://msedgedriver.azureedge.net/129.0.2792.86/edgedriver_linux64.zip -O /tmp/edgedriver_linux64.zip \
    && unzip /tmp/edgedriver_linux64.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/msedgedriver \
    && rm /tmp/edgedriver_linux64.zip

RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Generating Application Files" >> "$LOG_FILE"
# Copy application files
COPY . $APP_DIR/

RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Installing Python Packages" >> "$LOG_FILE"
# Install Python dependencies
RUN pip install -r requirements.txt && pip install debugpy

RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Mapping Volumes" >> "$LOG_FILE"
# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

RUN echo "$(date '+%Y-%m-%d %H:%M:%S') - Running the Application" >> "$LOG_FILE"
# Command to start our application
CMD ["python", "/srv/telegram_service/app/tgram_bot_runner.py"]
