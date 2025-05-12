import logging,json
from core import handler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event,context):
    text = ""
    token = ""
    language = ""

    logger.info(event)
    logger.info("Pre handler")
    body = json.loads(event['body'])
    
    if 'body' in event:
        text = body['message']
        token = body['token']
        language = body['language']
        mail = body['mail']
       
    else:
        text = event['message']
        token = event['token']
        language = event['language']
        mail = event['mail']

    if token == "":
        token = None
        
    if language == "":
        language = "ES"

    result = handler(text, token, language, mail)
    if isinstance(result, tuple) and len(result) == 2:
        response, new_token = result
    else:
        response = result
        new_token = None

    if new_token:
        message = {f"answer": response, "token": new_token}
    else:
        message = {f"answer": response}
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(message),
    }