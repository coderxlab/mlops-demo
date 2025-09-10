import os
from datetime import datetime

class Config:
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')
    
    # Kafka Configuration
    BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER', 'boot-vy2muewx.c1.kafka-serverless.ap-southeast-1.amazonaws.com:9098')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ml-features')
    KAFKA_BIN_PATH = os.getenv('KAFKA_BIN_PATH', '~/kafka_2.12-2.8.1/bin')
    
    # Feature Store Configuration
    FEATURE_GROUP_NAME = os.getenv('FEATURE_GROUP_NAME', f'kafka-customers-{datetime.now().strftime("%m-%d-%H-%M")}')
    S3_BUCKET_PREFIX = os.getenv('S3_BUCKET_PREFIX', 'sagemaker-')
    
    # Kafka Consumer/Producer Configuration
    CLIENT_PROPERTIES_FILE = 'client.properties'
    CONSUMER_TIMEOUT = int(os.getenv('CONSUMER_TIMEOUT', '10'))
    PRODUCER_TIMEOUT = int(os.getenv('PRODUCER_TIMEOUT', '30'))
    
    # Feature Store Schema
    REQUIRED_FIELDS = ['customer_id', 'product_id', 'order_amount', 'order_status', 'event_time']