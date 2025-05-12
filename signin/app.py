import logging,json
import psycopg2
import postgre
import bcrypt
import smtplib
import secrets
import string
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

POSTGRE_DB_HOST = "db-rdibot.claoesjfa0zq.us-east-1.rds.amazonaws.com"
POSTGRE_DB_PORT = "5432"
POSTGRE_DB_NAME = "postgres"
POSTGRE_DB_USER = "postgres"
POSTGRE_DB_PASS = "RDCom2024!!"

ENV = "lambda" 

def lambda_handler(event,context):
    try:

        mail = ""
        password = ""
        id = ""
        code = ""

        logger.info(event)
        logger.info("Pre handler")
        body = json.loads(event['body'])
        
        if 'body' in event:
            mail = body['mail']
            password = body['password']
            id = body['id']
            code = body['code']
        else:
            mail = event['mail']
            password = event['password']
            id = event['id']
            code = event['code']

        return signin(mail, password, id,code)
    
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


def signin(mail, password, id, code):
    try:
        print("llego a signin")
        
        # Valido que el código tenga licencias disponibles
        check_code = "select company_id, licences from public.companies where code = '" + code + "' and licences > 0"
        print("query licences", check_code)

        licences = readDB(check_code)
        
        print("query licences", licences)
        
        if licences[0][1] <= 0:
            return {
                "statusCode": 402,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("El código ingresado no tiene más licencias disponibles"),
            }
        
        print("paso check licencias")
        # Valido que el usuario no exista
        check_user= "select * from public.users_bot where mail = '" + mail + "'"
        user = readDB(check_user)
        if len(user) >= 1:
            return {
                "statusCode": 401,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("El mail ya se encuentran registrados en nuestra base de datos"),
            }
        
        # Hago el insert
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            token = token_generator()
            queries = []
            queries.append("INSERT INTO public.users_bot VALUES ('" + mail + "', '" + hashed_password + "', '" + id + "', '" + licences[0][0] + "','pending','"+ token +"','"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"');")
            queries.append("update public.companies set licences = licences - 1 where company_id = '" + licences[0][0] + "';")
            tran = True
            if send_email(mail,"RDiBot - Validación de Correo","Por favor, confirme su mail haciendo click en el siguiente link: https://rdibot.rdcom.app/validatemail?token=" + token + "&mail=" + mail):
                for query in queries:
                    tran = insertDB(query)
            if tran:
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                        "Access-Control-Allow-Methods": "OPTIONS,POST"
                    },
                    "body": json.dumps("El usuario fue creado correctamente"),
                }

        except Exception as error:
            logger.info(error)
            return None
        return None
    except:
        return None
    
def token_generator():
    # Define los caracteres que se pueden usar en el token
    caracteres = string.ascii_letters + string.digits
    # Genera un token aleatorio de la longitud especificada
    token = ''.join(secrets.choice(caracteres) for _ in range(16))
    return token
    
def send_email(recipient, subject, body):
    # Variables de entorno
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "it@rdcom.global"
    smtp_password = "nbftolgmfyqystqy"

    # Configuración del correo
    msg = MIMEMultipart()
    msg['From'] = "RDiBot"
    msg['To'] = recipient
    msg['Subject'] = subject

    # Cuerpo del correo
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Configuración del servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()  # Inicia TLS
        server.ehlo()
        server.login(smtp_user, smtp_password)
        
        # Envío del correo
        server.sendmail(smtp_user, recipient, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False  

def readDB(query, params = {}):
    print("llego a read DB")
    if ENV == "local":
        # Establecer la conexión con la base de datos
        conn = psycopg2.connect(
            database=POSTGRE_DB_NAME,
            user=POSTGRE_DB_USER,
            password=POSTGRE_DB_PASS,
            host=POSTGRE_DB_HOST,
            port=POSTGRE_DB_PORT
        )

        # Crear un cursor para ejecutar consultas SQL
        cur = conn.cursor()

        # Ejecutar una consulta de lectura
        if params:
            cur.execute(query,params)
        else:
            cur.execute(query)

        # Obtener los resultados de la consulta
        rows = cur.fetchall()

        # Mostrar los resultados
        # for row in rows:
        #     print(row)

        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()
    else:
        print("hace la query")
        rows = postgre.query_postgresql(query)
        print("Result query",rows)

    return rows

def insertDB(query):
    try:
        if ENV == "local":
            # Establecer la conexión con la base de datos
            conn = psycopg2.connect(
                database=POSTGRE_DB_NAME,
                user=POSTGRE_DB_USER,
                password=POSTGRE_DB_PASS,
                host=POSTGRE_DB_HOST,
                port=POSTGRE_DB_PORT
            )

            # Crear un cursor para ejecutar consultas SQL
            cur = conn.cursor()

            # Ejecutar una consulta de lectura
            cur.execute(query)

            # Obtener los resultados de la consulta
            rows = cur.fetchall()

            # Mostrar los resultados
            # for row in rows:
            #     print(row)

            # Cerrar el cursor y la conexión
            cur.close()
            conn.close()

        else:
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