import boto3

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='fake',
    aws_secret_access_key='fake'
)

table = dynamodb.create_table(
    TableName='CarQueries',
    KeySchema=[{'AttributeName': 'query_id', 'KeyType': 'HASH'}],
    AttributeDefinitions=[{'AttributeName': 'query_id', 'AttributeType': 'S'}],
    BillingMode='PAY_PER_REQUEST'
)
table.wait_until_exists()
print("OK:", table.table_status)
