import subprocess
import os
import json
from datetime import datetime
from config import Config

print("✅ Using EC2 IAM role for AWS access")

# Kafka configuration from config file
KAFKA_BIN = os.path.expanduser(Config.KAFKA_BIN_PATH)
BOOTSTRAP_SERVER = Config.BOOTSTRAP_SERVER
TOPIC = Config.KAFKA_TOPIC

def run_kafka_command(cmd):
    """Run kafka command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=KAFKA_BIN, 
                              capture_output=True, text=True, timeout=Config.PRODUCER_TIMEOUT)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_topic_creation():
    """Test creating topic"""
    print("Testing topic creation...")
    cmd = f"./kafka-topics.sh --create --bootstrap-server {BOOTSTRAP_SERVER} --replication-factor 3 --partitions 8 --topic {TOPIC} --command-config client.properties"
    
    success, stdout, stderr = run_kafka_command(cmd)
    if success or "already exists" in stderr:
        print("✅ Topic creation successful!")
        return True
    else:
        print(f"❌ Topic creation failed: {stderr}")
        return False

def test_producer():
    """Test sending messages"""
    print("Testing Kafka Producer...")
    
    # Create test messages
    messages = []
    for i in range(3):
        test_data = {
            'user_id': f'user_{i}',
            'feature_1': 85.5 + i,
            'feature_2': -12.3 - i,
            'feature_3': 'A',
            'EventTime': datetime.now().isoformat()
        }
        messages.append(json.dumps(test_data))
    
    # Send messages using echo and pipe
    message_input = "\n".join(messages)
    cmd = f"echo '{message_input}' | ./kafka-console-producer.sh --bootstrap-server {BOOTSTRAP_SERVER} --topic {TOPIC} --producer.config client.properties"
    
    success, stdout, stderr = run_kafka_command(cmd)
    if success:
        print("✅ Producer test successful!")
        for msg in messages:
            print(f"Sent: {msg}")
        return True
    else:
        print(f"❌ Producer failed: {stderr}")
        return False

def test_consumer():
    """Test reading messages"""
    print("Testing Kafka Consumer...")
    cmd = f"timeout {Config.CONSUMER_TIMEOUT} ./kafka-console-consumer.sh --bootstrap-server {BOOTSTRAP_SERVER} --topic {TOPIC} --consumer.config {Config.CLIENT_PROPERTIES_FILE} --from-beginning"
    
    success, stdout, stderr = run_kafka_command(cmd)
    if stdout.strip():
        print("✅ Consumer test successful!")
        print("Received messages:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                print(f"  {line}")
        return True
    else:
        print(f"❌ Consumer failed or no messages: {stderr}")
        return False

if __name__ == "__main__":
    # Check if kafka bin directory exists
    if not os.path.exists(KAFKA_BIN):
        print(f"❌ Kafka bin directory not found: {KAFKA_BIN}")
        exit(1)
    
    # Check if client.properties exists
    client_props = os.path.join(KAFKA_BIN, "client.properties")
    if not os.path.exists(client_props):
        print(f"❌ client.properties not found: {client_props}")
        exit(1)
    
    print(f"Using Kafka bin: {KAFKA_BIN}")
    
    # Run tests
    test_topic_creation()
    test_producer()
    test_consumer()