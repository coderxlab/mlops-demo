# Kafka to AWS SageMaker Feature Store on EC2

## What This Does

This project streams data from Kafka (Amazon MSK) into AWS SageMaker Feature Store for machine learning, running on EC2.

**Simple Flow**: Kafka Messages → Python Consumer (EC2) → AWS Feature Store

## Files Explained

- `msk_producer.py` - Sends sample data to MSK Serverless
- `kafka_feature_store_consumer.py` - Reads from MSK and saves to Feature Store
- `ec2_test.py` - Test MSK connection from EC2
- `ec2-setup.sh` - EC2 environment setup script
- `config.py` - Centralized configuration management
- `requirements.txt` - Python packages needed

## How It Works

### 1. Kafka (Message Queue)
- Think of it as a pipeline where data flows
- Messages are JSON data about users/features
- MSK is Amazon's managed Kafka service

### 2. Consumer (Python Script on EC2)
- Listens to Kafka messages 24/7
- Transforms data into Feature Store format
- Handles errors and retries

### 3. Feature Store (AWS Storage)
- Stores ML features for training models
- Two parts: Online (fast) + Offline (analytics)

## EC2 Deployment

### Step 1: MSK Cluster Setup & Launch EC2 Instance

**MSK Cluster Setup**: Follow the [AWS MSK Setup Guide](https://render.skillbuilder.aws/?module_id=PF9TTGHSCQ%3A001.000.000&product_id=V9JZ6N96HR%3A001.000.000&registration_id=5b32a51f-3230-50f4-94fd-ea7157725baf&navigation=digital) to create your MSK cluster and configure client machines.

### Step 2: Connect and Setup Environment
```bash
# SCP project files all files in code folder to EC2
scp -i your-key.pem -r kafka_feature_store_ec2/code ec2-user@your-ec2-ip:~

# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

cd code

# Run setup script
chmod +x ec2-setup.sh
./ec2-setup.sh
```

### Step 3: Configure Environment
```bash
# Copy and edit configuration
cp .env.template .env
nano .env

# Load environment variables
source .env
```

### Step 4: Test Connection
```bash
python3 ec2_test.py
```

### Step 5: Setup Feature Group
```bash
python3 setup_feature_group.py
```

### Step 6: Run Consumer
```bash
python3 kafka_feature_store_consumer.py
```

## Configuration

All settings are managed through environment variables in `.env` file:

```bash
# AWS Configuration
AWS_REGION=ap-southeast-1

# Kafka Configuration
BOOTSTRAP_SERVER=boot-vy2muewx.c1.kafka-serverless.ap-southeast-1.amazonaws.com:9098
KAFKA_TOPIC=ml-features
KAFKA_BIN_PATH=~/kafka_2.12-2.8.1/bin

# Feature Store Configuration
FEATURE_GROUP_NAME=kafka-customers-$(date +%m-%d-%H-%M)
```

## Sample Data Format

```json
{
  "customer_id": "C1234",
  "product_id": "P5678",
  "order_amount": 99.99,
  "order_status": "completed",
  "event_time": "2024-01-15T10:30:00Z"
}
```

