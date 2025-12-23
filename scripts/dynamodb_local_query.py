import boto3
from datetime import datetime
import json

# Connect to DynamoDB Local (running on localhost:8000)
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',  # Point to local Docker container
    region_name='us-east-1',
    aws_access_key_id='fakeMyKeyId',       # Fake credentials work locally
    aws_secret_access_key='fakeSecretAccessKey'
)

print("Connected to DynamoDB Local")

# Create test table
try:
    table = dynamodb.create_table(
        TableName='CarQueries',
        KeySchema=[
            {'AttributeName': 'query_id', 'KeyType': 'HASH'}  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'query_id', 'AttributeType': 'S'}  # String type
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print(f"Created table: {table.table_name}")
    table.wait_until_exists()
except Exception as e:
    print(f"Table may already exist: {e}")
    table = dynamodb.Table('CarQueries')

# Insert test data
test_query = {
    'query_id': 'test_123',
    'user_id': 'user_456',
    'criteria': json.dumps({
        'make': 'Mazda',
        'model': 'CX-3',
        'year_min': 2015,
        'price_max': 20000
    }),
    'email': 'test@example.com',
    'frequency': 'rate(1 day)',
    'active': True,
    'created_at': datetime.utcnow().isoformat()
}

table.put_item(Item=test_query)
print(f"Inserted item with query_id: {test_query['query_id']}")

# Retrieve and verify
response = table.get_item(Key={'query_id': 'test_123'})
print(f"\nRetrieved item:")
print(json.dumps(response['Item'], indent=2, default=str))

# List all items
print("\nScanning all items in table:")
scan_response = table.scan()
for item in scan_response['Items']:
    print(f"  - {item['query_id']}: {item.get('email')}")

print("\n✅ DynamoDB Local test successful!")
