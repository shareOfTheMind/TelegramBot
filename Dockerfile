# Use the specified Python version
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_DIR=/srv/telegram_service
ENV VENV_DIR=$APP_DIR/api_service_venv
ENV LOG_DIR=/var/log/tgram_bot_logging
ENV CONFIG_DIR=$APP_DIR/app/config

# Create necessary directories
RUN mkdir -p $APP_DIR $LOG_DIR $CONFIG_DIR

# Set working directory
WORKDIR $APP_DIR

# Install sudo to manage permissions and services
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up deployuser with correct permissions
RUN useradd -m deployuser && \
    mkdir -p $LOG_DIR && \
    chown -R deployuser:deployuser $APP_DIR $LOG_DIR $CONFIG_DIR && \
    chmod -R 775 $APP_DIR

# Grant deployuser sudo privileges for restarting services
RUN echo "deployuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart tgram.service, /usr/bin/systemctl daemon-reload" >> /etc/sudoers

# Copy application files and ensure deploy.sh and other necessary files are part of the setup
COPY . $APP_DIR/
COPY deploy.sh $APP_DIR/
COPY requirements.txt $APP_DIR/

# Create the virtual environment and activate it
RUN python -m venv $VENV_DIR && \
    chmod +x $VENV_DIR/bin/activate && \
    source $VENV_DIR/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Ensure correct permissions on the virtual environment and project files
RUN chmod +x $VENV_DIR/bin/activate $APP_DIR/deploy.sh

# Ensure that persistent logging is mapped to host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Set permissions for cookie_info.txt and ensure deployuser has the correct ownership for the whole directory
RUN chmod 644 $APP_DIR/cookie_info.txt && \
    chown -R deployuser:deployuser $APP_DIR

# Expose necessary ports (adjust if your app uses other ports)
EXPOSE 8080

# Switch to deployuser
USER deployuser

# Execute the deploy script and run the service
RUN chmod +x deploy.sh && ./deploy.sh

# Command to start the application
CMD ["sudo", "/usr/bin/systemctl", "restart", "tgram.service"]
