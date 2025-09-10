import json
import time
import subprocess
import os
from datetime import datetime
import random
from config import Config

class MSKDataProducer:
    def __init__(self):
        # MSK Serverless configuration
        self.bootstrap_server = Config.BOOTSTRAP_SERVER
        self.kafka_bin = os.path.expanduser(Config.KAFKA_BIN_PATH)
    
    def generate_sample_data(self):
        """Generate sample data matching Feature Store schema"""
        # Format timestamp for SageMaker Feature Store (ISO-8601 with Z)
        event_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return {
            'customer_id': f'C{random.randint(1000, 9999)}',
            'product_id': f'P{random.randint(1000, 9999)}',
            'order_amount': round(random.uniform(10.0, 999.99), 2),
            'order_status': random.choice(['completed', 'pending', 'cancelled']),
            'event_time': event_time
        }
    
    def send_data(self, topic=Config.KAFKA_TOPIC, num_messages=10):
        """Send sample data to MSK topic"""
        messages = []
        for i in range(num_messages):
            data = self.generate_sample_data()
            messages.append(json.dumps(data))
            print(f"Generated message {i+1}: {data}")
        
        # Send all messages at once
        message_input = "\n".join(messages)
        cmd = f"echo '{message_input}' | ./kafka-console-producer.sh --bootstrap-server {self.bootstrap_server} --topic {topic} --producer.config {Config.CLIENT_PROPERTIES_FILE}"
        
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=self.kafka_bin,
                capture_output=True, text=True, timeout=Config.PRODUCER_TIMEOUT
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully sent {num_messages} messages to topic '{topic}'")
            else:
                print(f"❌ Error sending messages: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Producer command timed out")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    producer = MSKDataProducer()
    producer.send_data()