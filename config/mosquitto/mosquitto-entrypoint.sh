#!/bin/sh

# Enable verbose output
set -x

# Debugging info: Print environment variables
echo "MOSQUITTO_USERNAME=${MOSQUITTO_USERNAME}"
echo "MOSQUITTO_PASSWORD=${MOSQUITTO_PASSWORD}"

# Create the password file from environment variables
if [ -n "$MOSQUITTO_USERNAME" ] && [ -n "$MOSQUITTO_PASSWORD" ]; then
  echo "Creating Mosquitto password file."
  touch /mosquitto/config/password_file
  mosquitto_passwd -b /mosquitto/config/password_file $MOSQUITTO_USERNAME $MOSQUITTO_PASSWORD
  echo "Password file created successfully."
else
  echo "Environment variables MOSQUITTO_USERNAME and MOSQUITTO_PASSWORD must be set."
  exit 1
fi

# Ensure the log directory exists and has the correct permissions
echo "Ensuring /mosquitto/logs directory exists and has correct permissions."
mkdir -p /mosquitto/logs
chmod 0777 /mosquitto/logs
ls -ld /mosquitto/logs

# Debugging info: Print contents of the config directory
echo "Contents of /mosquitto/config directory:"
ls -l /mosquitto/config

# Start Mosquitto and capture output
echo "Starting Mosquitto..."
mosquitto -c /mosquitto/config/mosquitto.conf &
MOSQUITTO_PID=$!
echo "Mosquitto PID: $MOSQUITTO_PID"

# Wait for Mosquitto to start
sleep 5

# Check if Mosquitto is running by examining the logs
if grep -q "mosquitto version" /mosquitto/logs/mosquitto.log; then
  echo "Mosquitto started successfully."
else
  echo "Mosquitto failed to start."
  cat /mosquitto/logs/mosquitto.log
  exit 1
fi

# Keep the container running for debugging
tail -f /dev/null
