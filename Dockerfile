# Use the specified Python version
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_DIR=/srv/telegram_service
ENV VENV_DIR=$APP_DIR/api_service_venv
ENV LOG_DIR=/srv/telegram_service/logs
ENV CONFIG_DIR=$APP_DIR/app/config

# Create necessary directories
RUN mkdir -p $APP_DIR $LOG_DIR $CONFIG_DIR

# Set working directory
WORKDIR $APP_DIR

# Install necessary packages
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up deployuser with correct permissions
RUN useradd -m deployuser && \
    chown -R deployuser:deployuser $APP_DIR $LOG_DIR $CONFIG_DIR && \
    chmod -R 775 $APP_DIR

# Grant deployuser sudo privileges for restarting services
RUN echo "deployuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart tgram.service, /usr/bin/systemctl daemon-reload" >> /etc/sudoers

# Copy application files
COPY . $APP_DIR/

# Create the virtual environment and install dependencies
RUN python -m venv $VENV_DIR && \
    $VENV_DIR/bin/pip install --upgrade pip && \
    $VENV_DIR/bin/pip install -r requirements.txt

# Ensure correct permissions on the virtual environment and project files
RUN chown -R deployuser:deployuser $APP_DIR

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Switch to deployuser
USER deployuser

# Command to run the deploy.sh script
CMD ["bash", "$APP_DIR/deploy.sh"]
