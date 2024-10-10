# Use the specified Python version
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_DIR=/srv/telegram_service
ENV VENV_DIR=$APP_DIR/api_service_venv
ENV LOG_DIR=$APP_DIR/logs
ENV CONFIG_DIR=$APP_DIR/app/config

# Install required dependencies for msedgedriver and other tools
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libxcb1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxrender1 \
    libdbus-1-3 \
    libxtst6 \
    libgtk-3-0 \
    libatspi2.0-0 \
    libxshmfence1 \
    libgbm1 \
    libasound2



# Set working directory
WORKDIR $APP_DIR

# Copy application files
COPY . $APP_DIR/

RUN pip install -r requirements.txt

# Ensure that persistent logging is mapped to the host system
VOLUME ["$LOG_DIR", "$CONFIG_DIR/.env"]

# Command to start our application
CMD python $APP_DIR/app/tgram_bot_runner.py
