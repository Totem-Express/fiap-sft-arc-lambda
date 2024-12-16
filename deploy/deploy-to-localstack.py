import subprocess
import boto3
import os

api_gateway_client = boto3.client('apigateway')
lambda_client = boto3.client('lambda')

def get_build_path():
    current = os.getcwd()
    if current.endswith("deploy"):
        return os.path.normpath(current + os.sep + os.pardir)
    
    return current

def create_api_gateway():
    gateway = api_gateway_client.create_rest_api(
        name='totem-lambda',
        endpointConfiguration= {
            'types': ['EDGE']
        },
        
    )

    return gateway['id']

def create_api_gateway_auth_resource():
    gateway_id = create_api_gateway()
    
    root_resource = api_gateway_client.get_resources(
        restApiId = gateway_id
    )

    root_resource_id = root_resource['items'][0]['id']
    
    resource_response = api_gateway_client.create_resource(
        restApiId=gateway_id,
        parentId=root_resource_id,
        pathPart="auth"
    )

    return gateway_id, resource_response['id']

def create_lambda():
    base_path = get_build_path()
    path = f"{base_path}/target/uberjar/totem-auth-1.0-standalone.jar"
    
    with open(path, 'rb') as function_code:
        lambda_client.create_function(
            FunctionName="AuthHandler",
            Runtime="java11",
            Role="arn:aws:iam::123456789012:role/lambda-role",
            Handler="totem_auth.core",
            Code={
                'ZipFile': function_code.read()
            },
            Timeout=30,
            MemorySize=256,
            Environment={
                'Variables': {
                    'DB_URL': 'jdbc:mysql://localhost:3306/totemexpress',
                    'DB_USER': 'totemexpress',
                    'DB_PASSWORD': 'secret'
                }
            }
        )

def create_integration(api_id, resource_id):
    lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:AuthHandler/invocations"

    api_gateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='OPTIONS'
    )

    api_gateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='NONE'
    )

    api_gateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=lambda_uri
    )

    api_gateway_client.create_deployment(
        restApiId=api_id,
        stageName='dev'
    )

def deploy():
    api_id, resource_id = create_api_gateway_auth_resource()
    create_lambda()
    create_integration(api_id=api_id, resource_id=resource_id)

    return api_id

def build_lambda_fn():
    lein_directory = get_build_path()
    subprocess.run(["lein", "uberjar"], cwd=lein_directory, check = True)

def main():
    build_lambda_fn()
    api = deploy()
    print(f"The Api Gateway is Avaiable at: http://localhost:4566/restapis/{api}/dev/_user_request_/auth")

if __name__ == '__main__':
    main()