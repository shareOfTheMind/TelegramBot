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

# Install required packages for downloading and installing Microsoft Edge
# RUN apt-get update && apt-get install -y \
#     gpg \
#     wget \
#     gnupg \
#     apt-transport-https \
#     unzip \
#     && apt-get clean

# # Download and install Microsoft Edge
# RUN wget https://packages.microsoft.com/keys/microsoft.asc -O microsoft.asc \
#     && gpg --dearmor microsoft.asc -o /usr/share/keyrings/microsoft.gpg \
#     && echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
#     && apt-get update \
#     && apt-get install -y microsoft-edge-stable \
#     && rm microsoft.asc

# # Download the specific version of msedgedriver
# RUN wget -q https://msedgedriver.azureedge.net/130.0.2849.19/edgedriver_linux64.zip -O /tmp/edgedriver_linux64.zip \
#     && unzip /tmp/edgedriver_linux64.zip -d /usr/local/bin/ \
#     && chmod +x /usr/local/bin/edgedriver \
#     && rm /tmp/edgedriver_linux64.zip

# Copy application files
COPY . $APP_DIR/

# Install Python dependencies
RUN pip install -r requirements.txt

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Command to start our application
CMD python $APP_DIR/app/tgram_bot_runner.py
