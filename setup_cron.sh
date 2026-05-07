#!/bin/bash

# Get the absolute path to the directory and python executable
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_BIN="$(which python3)"

if [ -z "$PYTHON_BIN" ]; then
    echo "Python3 not found. Please ensure it is installed."
    exit 1
fi

# The cron job command: runs every day at 8:00 AM
# We cd into the directory first so that .env loads correctly
CRON_JOB="0 8 * * * cd $DIR && $PYTHON_BIN $DIR/briefing.py >> $DIR/briefing.log 2>&1"

# Check if the job already exists
(crontab -l 2>/dev/null | grep -F "$DIR/briefing.py") > /dev/null
if [ $? -eq 0 ]; then
    echo "Cron job already exists! The Morning Briefing is already scheduled."
else
    # Add the new job to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Successfully scheduled the Morning Briefing to run every day at 8:00 AM!"
    echo "Logs will be written to: $DIR/briefing.log"
fi
