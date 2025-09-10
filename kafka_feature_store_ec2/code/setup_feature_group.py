import sagemaker
import pandas as pd
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.feature_store.inputs import TableFormatEnum
from datetime import datetime
import time
import boto3
from config import Config

def create_feature_group_for_kafka():
    """Create a feature group for Kafka data ingestion"""
    
    # Initialize SageMaker session for EC2
    boto_session = boto3.Session(region_name=Config.AWS_REGION)
    sagemaker_session = sagemaker.Session(boto_session=boto_session)

    print(f'SageMaker session: {sagemaker_session}')
    # Get role ARN using SageMaker
    role_arn = sagemaker.get_execution_role()
    print(f'Role ARN: {role_arn}')
    
    default_bucket = sagemaker_session.default_bucket()
    
    # Create sample data to define schema
    sample_data = {
        'customer_id': ['C1001'],
        'product_id': ['P1001'], 
        'order_amount': [99.99],
        'order_status': ['completed'],
        'event_time': [datetime.now().isoformat()]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Convert to string types for Feature Store
    df['customer_id'] = df['customer_id'].astype('string')
    df['product_id'] = df['product_id'].astype('string') 
    df['event_time'] = df['event_time'].astype('string')
    
    # Create feature group name with timestamp
    feature_group_name = Config.FEATURE_GROUP_NAME
    
    # Initialize feature group
    feature_group = FeatureGroup(
        name=feature_group_name,
        sagemaker_session=sagemaker_session
    )
    
    # Load feature definitions
    feature_group.load_feature_definitions(data_frame=df)
    
    print(f"Creating feature group: {feature_group_name}")
    print(f"Using role: {role_arn}")
    
    # Create feature group
    feature_group.create(
        s3_uri=f's3://{default_bucket}/feature-store',
        record_identifier_name='customer_id',
        event_time_feature_name='event_time',
        role_arn=role_arn,
        enable_online_store=True,
        table_format=TableFormatEnum.ICEBERG
    )
    
    # Wait for creation
    status = feature_group.describe().get('FeatureGroupStatus')
    print(f'Initial status: {status}')
    
    while status == 'Creating':
        print('Waiting for feature group creation...')
        time.sleep(10)
        status = feature_group.describe().get('FeatureGroupStatus')
    
    if status == 'Created':
        print(f'✅ Feature group {feature_group_name} created successfully!')
        print(f'Use this name in your Kafka consumer: {feature_group_name}')
        return feature_group_name
    else:
        print(f'❌ Failed to create feature group. Status: {status}')
        return None

if __name__ == "__main__":
    feature_group_name = create_feature_group_for_kafka()
    
    if feature_group_name:
        print("\n" + "="*50)
        print("SETUP COMPLETE!")
        print("="*50)
        print(f"Feature Group Name: {feature_group_name}")
        print("\nTo use with your Kafka consumer:")
        print(f"export FEATURE_GROUP_NAME={feature_group_name}")
        print("export MSK_ENDPOINT=your-msk-endpoint:9092")
        print("export KAFKA_TOPIC=your-topic-name")
        print("\nThen run: python simple_kafka_consumer.py")