#!/bin/bash
# Deploy wrapper script for SSH command restriction
# This script limits what commands can be executed via SSH for security

set -e

# Log directory and file
LOG_DIR="/home/deploy/logs"
LOG_FILE="${LOG_DIR}/deploy.log"

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Log the command
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploy command: $SSH_ORIGINAL_COMMAND" >> "${LOG_FILE}"

# Only allow specific commands
case "$SSH_ORIGINAL_COMMAND" in
    # Allow deploy.sh with version parameter
    "cd /home/deploy/api-server"$'\n'"./deploy.sh"*)
        cd /home/deploy/api-server && eval "${SSH_ORIGINAL_COMMAND#*$'\n'}"
        ;;
    "cd /home/deploy/api-server && ./deploy.sh"*)
        cd /home/deploy/api-server && eval "${SSH_ORIGINAL_COMMAND#cd /home/deploy/api-server && }"
        ;;

    # Allow docker compose commands in api-server directory
    "cd /home/deploy/api-server/guanfu_backend"$'\n'"docker compose"*)
        cd /home/deploy/api-server/guanfu_backend && eval "${SSH_ORIGINAL_COMMAND#*$'\n'}"
        ;;
    "cd /home/deploy/api-server/guanfu_backend && docker compose"*)
        cd /home/deploy/api-server/guanfu_backend && eval "${SSH_ORIGINAL_COMMAND#cd /home/deploy/api-server/guanfu_backend && }"
        ;;

    # Allow docker status and log viewing
    "docker ps"*|"docker compose ps"*)
        $SSH_ORIGINAL_COMMAND
        ;;
    "docker logs"*|"docker compose logs"*)
        $SSH_ORIGINAL_COMMAND
        ;;

    # Allow health checks
    "curl"*)
        $SSH_ORIGINAL_COMMAND
        ;;

    # Deny all other commands
    *)
        echo "ERROR: Command not allowed: $SSH_ORIGINAL_COMMAND" >&2
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] DENIED: $SSH_ORIGINAL_COMMAND" >> "${LOG_FILE}"
        exit 1
        ;;
esac

# Log success
echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: Command completed" >> "${LOG_FILE}"
