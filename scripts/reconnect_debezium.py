import urllib.request
import urllib.error
import json
import os

DEBEZIUM_URL = "http://localhost:8083/connectors"
SOURCE_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../configs/register-source-connector.json"))
STAGING_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../configs/register-staging-connector.json"))

def make_request(url, method="GET", data=None):
    headers = {"Content-Type": "application/json"}
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            err_json = json.loads(body)
        except:
            err_json = body
        return e.code, err_json
    except Exception as e:
        return 500, str(e)

def delete_connector(name):
    print(f"Deleting connector '{name}' if exists...")
    code, resp = make_request(f"{DEBEZIUM_URL}/{name}", method="DELETE")
    if code in (200, 204):
        print(f"Successfully deleted connector '{name}'.")
    elif code == 404:
        print(f"Connector '{name}' did not exist.")
    else:
        print(f"Failed to delete connector '{name}': Code {code}, Response: {resp}")

def create_connector(config_path):
    print(f"Reading configuration from {config_path}...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    name = config.get("name")
    print(f"Registering connector '{name}'...")
    code, resp = make_request(DEBEZIUM_URL, method="POST", data=config)
    if code in (200, 201):
        print(f"Successfully registered connector '{name}'!")
    else:
        print(f"Failed to register connector '{name}': Code {code}, Response: {resp}")

def main():
    print("=== DEBEZIUM CONNECTOR RECONNECT SCRIPT ===")
    
    # 1. Delete both connectors first to force clean replication setup
    delete_connector("postgresql-source-connector")
    delete_connector("postgresql-staging-connector")
    
    # 2. Register connectors
    create_connector(SOURCE_CONFIG_PATH)
    create_connector(STAGING_CONFIG_PATH)
    
    # 3. Verify active connectors
    code, resp = make_request(DEBEZIUM_URL)
    if code == 200:
        print(f"Active Debezium Connectors: {resp}")
    else:
        print(f"Failed to fetch active connectors list: Code {code}")

if __name__ == '__main__':
    main()
