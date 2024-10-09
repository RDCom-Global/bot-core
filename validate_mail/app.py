import logging,json
import psycopg2
import postgre
import bcrypt
import smtplib
import secrets
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event,context):
    try:
        mail = ""
        internal_token = ""
     
        body = json.loads(event['body'])
        
        if 'body' in event:
            mail = body['mail']
            internal_token = body['internal_token']
        else:
            mail = event['mail']
            internal_token = event['internal_token']
        return validate(mail, internal_token)
    
    except Exception as error:
        logger.info(error)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps("Hubo un error"),
        }


def validate(mail,token):
    try:
        logger.info(mail)
        logger.info(token)

        # Valido que el token exista
        token_date_query = "select token_date from public.users_bot where mail = '" + mail + "' and token = '"+ token+"'"
        token_date = readDB(token_date_query)
        if len(token_date) <= 0:
            return {
                "statusCode": 402,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("El código ingresado no tiene más licencias disponibles"),
            }
        
        datecomplete = datetime.combine(token_date[0][0], datetime.min.time())
        if datecomplete >= datetime.now() - timedelta(days=7):
            logger.info(token_date)
            update_user = "update users_bot set status = 'active' where mail = '"+ mail+"'"
            result = insertDB(update_user)
            if result:
                
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                        "Access-Control-Allow-Methods": "OPTIONS,POST"
                    },
                    "body": json.dumps("El usuario fue validado correctamente"),
                }
    except Exception as error:
        logger.info(error)
        return None
    

def readDB(query):
    rows = postgre.query_postgresql(query)
    return rows

def insertDB(query):
    try:
        rows = postgre.insert_postgresql(query)
        return rows
    except:
        return None
    
def insertTransactionDB(queries):
    try:
        rows = postgre.transaction_postresql(queries)
        return rows
    except:
        return None