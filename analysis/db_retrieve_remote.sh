#!/bin/bash

# Define remote host, directory, and username
REMOTE_HOST="propilot.khoury.northeastern.edu"
REMOTE_USER="vdswain"
REMOTE_DIR="/home/clippy/pro-pilot/data/"
LOCAL_DIR="../data/server_data/"

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

# Copy all .tsv files from remote directory to local directory
scp "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR*.tsv" "$LOCAL_DIR"