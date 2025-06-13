# Función Lambda – Consulta API Redeban

## Descripción
Esta función Lambda realiza una consulta a la API de Redeban utilizando token almacenado en DynamoDB y autenticación mTLS con certificados cliente desde Secrets Manager.

## Servicios utilizados
- AWS Lambda
- AWS Secrets Manager
- AWS DynamoDB

## Estructura esperada
### Secrets Manager: `Redeban_Obtener_Token`
- `redeban_crt`: Certificado del cliente (Base64)
- `redeban_key`: Llave privada del cliente (Base64)

### DynamoDB: Tabla `RedebanTokens`
- PK: `id = token`
- Atributo: `access_token` con el valor Bearer

## Instrucciones
1. Subir certificados a Secrets Manager
2. Cargar token en DynamoDB
3. Comprimir `lambda_function.py` en un ZIP
4. Crear función Lambda en AWS con Runtime Python 3.11
5. Asignar permisos para Secrets Manager y DynamoDB (GetSecretValue, GetItem)
6. Ejecutar test en Lambda

## Notas de seguridad
- Este script desactiva la verificación SSL (`CERT_NONE`) solo para entorno de pruebas.