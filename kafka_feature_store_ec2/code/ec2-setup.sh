#!/bin/bash

# Install Python and pip
sudo yum update -y
sudo yum install -y python3 python3-pip

# Go to project directory
cd ~/kafka_feature_store

# Install dependencies
pip3 install -r requirements.txt

# Set AWS region from config
export AWS_DEFAULT_REGION=${AWS_REGION:-ap-southeast-1}

echo "Setup complete! Run: python3 ec2_test.py"