#!/bin/bash

# Configuration
KEY_PATH="~/.ssh/jobfitcv-bastion-key.pem"
BASTION_USER="ec2-user"
BASTION_IP="98.84.125.213"
RDS_ENDPOINT="jobfitcv-postgres.cuzwwyy28wm9.us-east-1.rds.amazonaws.com"
DB_USER="jobfitcv"
DB_NAME="jobfitcv"

echo "🏃 Jumping to EC2 and connecting to RDS..."

ssh -i $KEY_PATH $BASTION_USER@$BASTION_IP -t "psql -h $RDS_ENDPOINT -U $DB_USER -d $DB_NAME"
