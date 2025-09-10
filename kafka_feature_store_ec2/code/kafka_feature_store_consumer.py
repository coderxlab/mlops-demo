import json
import boto3
import subprocess
import os
from datetime import datetime
from config import Config

class KafkaFeatureStoreConsumer:
    def __init__(self, kafka_config, feature_group_name, region=Config.AWS_REGION):
        self.kafka_config = kafka_config
        self.feature_group_name = feature_group_name
        self.sagemaker_client = boto3.client('sagemaker-featurestore-runtime', region_name=region)
        self.kafka_bin = os.path.expanduser(Config.KAFKA_BIN_PATH)
        
    def process_message(self, message_json):
        """Transform Kafka message to Feature Store format"""
        try:
            data = json.loads(message_json)
            
            # Ensure all required fields match Feature Store schema
            required_fields = Config.REQUIRED_FIELDS
            
            # Validate schema
            for field in required_fields:
                if field not in data:
                    print(f"Missing required field: {field}")
                    return None
            
            # Convert to Feature Store format
            record = {
                'customer_id': str(data['customer_id']),
                'product_id': str(data['product_id']),
                'order_amount': str(data['order_amount']),
                'order_status': str(data['order_status']),
                'event_time': str(data['event_time'])
            }
            
            return record
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def ingest_to_feature_store(self, record):
        """Ingest single record to Feature Store"""
        try:
            response = self.sagemaker_client.put_record(
                FeatureGroupName=self.feature_group_name,
                Record=[
                    {'FeatureName': k, 'ValueAsString': v} 
                    for k, v in record.items()
                ]
            )
            return response
        except Exception as e:
            print(f"Error ingesting record: {e}")
            return None
    
    def start_consuming(self):
        """Start consuming messages from Kafka and ingest to Feature Store"""
        bootstrap_server = self.kafka_config['bootstrap_servers'][0]
        topic = self.kafka_config['topic']
        
        cmd = f"./kafka-console-consumer.sh --bootstrap-server {bootstrap_server} --topic {topic} --consumer.config {Config.CLIENT_PROPERTIES_FILE} --from-beginning"
        
        print(f"Starting consumer for topic: {topic}")
        print(f"Feature Group: {self.feature_group_name}")
        
        try:
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.kafka_bin,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    print(f"Received message: {line}")
                    processed_record = self.process_message(line)
                    if processed_record:
                        result = self.ingest_to_feature_store(processed_record)
                        if result:
                            print(f"✅ Successfully ingested record for customer: {processed_record['customer_id']}")
                        else:
                            print(f"❌ Failed to ingest record")
                    
        except KeyboardInterrupt:
            print("Consumer stopped")
            process.terminate()
        except Exception as e:
            print(f"Error in consumer: {e}")
        finally:
            if 'process' in locals():
                process.terminate()

if __name__ == "__main__":
    # Configuration
    kafka_config = {
        'topic': Config.KAFKA_TOPIC,
        'bootstrap_servers': [Config.BOOTSTRAP_SERVER]
    }
    
    # Use the feature group name from setup
    feature_group_name = Config.FEATURE_GROUP_NAME
    
    consumer = KafkaFeatureStoreConsumer(
        kafka_config=kafka_config,
        feature_group_name=feature_group_name
    )
    
    consumer.start_consuming()