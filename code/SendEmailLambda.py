import json
import boto3
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        order_id = event['order_id']
        customer_email = event['customer_email']
        
        # Publish order confirmation to SNS topic
        sns.publish(
            TopicArn='arn:aws:sns:ap-south-1:480482295683:OrderConfirmationTopic',
            Message=f"Your order {order_id} has been placed!",
            MessageAttributes={
                'CustomerEmail': {
                    'DataType': 'String',
                    'StringValue': customer_email
                }
            }
        )
        
        logger.info(f"Successfully published to OrderConfirmationTopic")

        return {
            'statusCode': 200,
            'body': json.dumps('Order confirmation sent successfully')
        }
        
    except ClientError as e:
        logger.error(f"ClientError for order_id {event.get('order_id')}: {str(e)}")
        # Publish error to SNS for alerting
        sns.publish(
            TopicArn='arn:aws:sns:ap-south-1:480482295683:OrderProcessingAlerts',
            Message=f"SendEmail failed for order {event.get('order_id')}: {str(e)}"
        )
        raise e  # Let Lambda send the event to DLQ