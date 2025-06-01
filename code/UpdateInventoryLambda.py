import json
import boto3
from botocore.exceptions import ClientError
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('InventoryTransactions')

def lambda_handler(event, context):
    try:
        # Parse input
        order_id = event['order_id']
        item_id = event['item_id']
        quantity = event['quantity']
        
        logger.info(f"Processing order_id: {order_id}, item_id: {item_id}, quantity: {quantity}")
        # Log inventory transaction
        table.put_item(Item={
            'order_id': order_id,
            'item_id': item_id,
            'quantity': quantity,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        
        logger.info(f"Successfully wrote to InventoryTransactions")

        return {
            'statusCode': 200,
            'body': json.dumps('Order Successfully wrote to InventoryTransactions')
        }

    except ClientError as e:
        # Publish error to SNS for alerting
        sns.publish(
            TopicArn='arn:aws:sns:ap-south-1:480482295683:OrderProcessingAlerts',
            Message=f"UpdateInventory failed for order {event.get('order_id')}: {str(e)}"
        )
        raise e  # Let Lambda send the event to DLQ