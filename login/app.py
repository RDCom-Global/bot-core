import logging,json
import psycopg2
import postgre
import bcrypt

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

        logger.info(event)
        logger.info("Pre handler")
        body = json.loads(event['body'])
        
        if 'body' in event:
            mail = body['mail']
            password = body['password']

        else:
            mail = event['mail']
            password = event['password']


        return login(mail, password)
    
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


def login(mail, password):
    try:
        # Valido que el usuario exista
        check_user= "select password from public.users_bot where mail = '" + mail + "'"
        print(check_user)
        user = readDB(check_user)
        if len(user) >= 1:
            stored_hash = user[0][0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                        "Access-Control-Allow-Methods": "OPTIONS,POST"
                    },
                    "body": json.dumps("Acceso correcto"),
                }
            else:
                return {
                    "statusCode": 401,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                        "Access-Control-Allow-Methods": "OPTIONS,POST"
                    },
                    "body": json.dumps("Acceso incorrecto"),
                }
        else:
            return {
                "statusCode": 401,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("Acceso incorrecto"),
            }
    except:
        return None
    

def readDB(query):
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
        rows = postgre.query_postgresql(query)

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