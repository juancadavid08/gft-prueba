import boto3
import base64
import json
import os
import urllib3
import logging
logging.basicConfig(level=logging.INFO)
import uuid
from datetime import datetime


REGION_NAME = "us-east-1"
SECRET_NAME = "Redeban_Obtener_Token"
CLIENT_SECRET_NAME = "Client_secrets_Rdb"
DYNAMODB_TABLE_NAME = "RedebanTokens"
MERCHANT_ID = "10203040"
TOKEN_ID = "token"

def obtener_certificados_de_secrets_manager(secret_name):
    client = boto3.client("secretsmanager", region_name=REGION_NAME)
    response = client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(response["SecretString"])

    cert_path = "/tmp/redeban.crt"
    key_path = "/tmp/redeban.key"

    with open(cert_path, "wb") as cert_file:
        cert_file.write(base64.b64decode(secret_dict["redeban_crt"]))

    with open(key_path, "wb") as key_file:
        key_file.write(base64.b64decode(secret_dict["redeban_key"]))

    return cert_path, key_path

def obtener_token_desde_dynamodb():
    dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={"id": TOKEN_ID})

    if "Item" not in response:
        raise Exception(f"Token no encontrado para MerchantID {TOKEN_ID}")

    return response["Item"]["access_token"]

def lambda_handler(event, context):
    try:
        logging.info("Obteniendo certificados...")
        cert_path, key_path = obtener_certificados_de_secrets_manager(SECRET_NAME)

        logging.info("Obteniendo token...")
        token = obtener_token_desde_dynamodb()

        logging.info("Token obtenido."+token)

        logging.info("Preparando conexión HTTPS...")
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            raise Exception("No se pudieron guardar correctamente los certificados.")
        http = urllib3.PoolManager(
            cert_file=cert_path,
            key_file=key_path,
            cert_reqs='CERT_NONE'
        )

        url = f"https://api.qa.sandboxhubredeban.com:9445/rbmcalidad/calidad/api/kyc/v3.0.0/enterprise/Commerce/{MERCHANT_ID}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "X-Forwarded-For": "10.0.0.1",
            "RBM-FROM": "218f3105-811f-4713-9818-8c7031e43c01",  
            "X-Request-ID": str(uuid.uuid4()),
            "Origin": "app.mibanco.com:8080",
            "RBMURI": "P2P", 
            "Geolocation": "+04.6534-074.0836",
            "X-Device-Fingerprint": str(uuid.uuid4())
        }

        logging.info("Realizando petición externa...")
        response = http.request("GET", url, headers=headers)

        logging.info("Respuesta recibida.")
        return {
            "statusCode": response.status,
            "body": response.data.decode("utf-8")
        }

    except Exception as e:
        logging.error("Error en ejecución", exc_info=True)
        return {
            "statusCode": 500,
            "body": str(e)
        }