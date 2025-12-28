#!/bin/bash

# Configuration
KEY_PATH="~/.ssh/jobfitcv-bastion-key.pem"
BASTION_USER="ec2-user"
BASTION_IP="98.84.125.213"
RDS_ENDPOINT="jobfitcv-postgres.cuzwwyy28wm9.us-east-1.rds.amazonaws.com"
LOCAL_PORT=5433 # Using 5433 to avoid conflict with local Postgres

echo "🚀 Opening SSH Tunnel to RDS via Bastion..."
echo "🔗 Local Port: $LOCAL_PORT -> RDS:5432"

ssh -i $KEY_PATH -L $LOCAL_PORT:$RDS_ENDPOINT:5432 $BASTION_USER@$BASTION_IP -N
