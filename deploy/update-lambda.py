import boto3
import subprocess
import os

client = boto3.client('lambda')

def get_build_path():
    current = os.getcwd()
    if current.endswith("deploy"):
        return os.path.normpath(current + os.sep + os.pardir)
    
    return current

def build_lambda_fn():
    lein_directory = get_build_path()
    subprocess.run(["lein", "uberjar"], cwd=lein_directory, check = True)

def update_lambda():
    base_path = get_build_path()
    path = f"{base_path}/target/uberjar/totem-auth-1.0-standalone.jar"
    with open(path, 'rb') as function_code:
        response = client.update_function_code(
            FunctionName="AuthHandler",
            ZipFile=function_code.read()
        )
        print(response)

if __name__ == '__main__':
    build_lambda_fn()
    update_lambda()