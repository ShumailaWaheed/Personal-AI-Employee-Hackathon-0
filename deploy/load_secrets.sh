#!/bin/bash
# Load secrets from GCP Secret Manager into .env.runtime
# Requires: gcloud CLI + instance IAM role: Secret Manager Secret Accessor

set -euo pipefail

SECRET_NAME="${GCP_SECRET_NAME:-ai-employee-env}"
PROJECT_ID="${GCP_PROJECT_ID:-}"

if [ -z "$PROJECT_ID" ]; then
    echo "GCP_PROJECT_ID not set. Falling back to local .env file."
    if [ -f /app/.env ]; then
        echo "Using existing /app/.env"
    else
        echo "WARNING: No .env file found. Copy .env.example to .env and fill in values."
    fi
    exit 0
fi

# Fetch secret and write to runtime env file
gcloud secrets versions access latest \
    --secret="$SECRET_NAME" \
    --project="$PROJECT_ID" > /app/.env.runtime

chmod 600 /app/.env.runtime

# Symlink as .env so python-dotenv picks it up
ln -sf /app/.env.runtime /app/.env

echo "Secrets loaded from GCP Secret Manager: $SECRET_NAME"
