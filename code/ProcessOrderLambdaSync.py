import json
import boto3
import time 
from botocore.exceptions import ClientError
import logging

# Initialize you log configuration using the base class
logging.basicConfig(level = logging.INFO)

# Retrieve the logger instance
logger = logging.getLogger()



dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
inventory_table = dynamodb.Table('Inventory')

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        print("Received json.dumps(event)")
        print(json.dumps(event))
        # Parse input from API Gateway
        #body = json.loads(event['body'])

        item_id = event['item_id']
        quantity = event['quantity']
        customer_email = event['customer_email']
        order_id = f"ORD-{int(time.time())}"  # Simple order ID based on timestamp

        # Check inventory in DynamoDB
        response = inventory_table.get_item(Key={'item_id': item_id})
        item = response.get('Item')
        
        if not item or item['quantity'] < quantity:
            logger.info(f"Item out of stock for item_id: {item_id}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Item out of stock'})
            }
        
        # Reserve inventory
        inventory_table.update_item(
            Key={'item_id': item_id},
            UpdateExpression='SET quantity = quantity - :val',
            ExpressionAttributeValues={':val': quantity}
        )
        
        # Trigger UpdateInventory sync
        update_response = lambda_client.invoke(
            FunctionName='UpdateInventoryLambda',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'order_id': order_id,
                'item_id': item_id,
                'quantity': quantity
            })
        )
        
        update_result = json.loads(update_response['Payload'].read().decode('utf-8'))
        logger.info(f"UpdateInventory response: {update_result}")
        logger.info(f"Invoked UpdateInventory for order_id: {order_id}")
        print('update_result')
        print(update_result)
        
        # Trigger SendEmail sync
        email_response=lambda_client.invoke(
            FunctionName='SendEmailLambda',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'order_id': order_id,
                'customer_email': customer_email
            })
        )
        
        email_result = json.loads(email_response['Payload'].read().decode('utf-8'))
        logger.info(f"SendEmail response: {email_result}")
        logger.info(f"Invoked SendEmail for order_id: order_id")
        print('email_result')
        print(email_result)
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'order_id': order_id,
                'status': 'Order confirmed'
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }