import re
from urllib.parse import quote_plus

def parse_mssql_connection_string(ms_conn_str):
    # Regular expression pattern to extract the necessary components
    pattern = r"Driver=\{(.*?)\};Server=(.*?);Database=(.*?);Uid=(.*?);Pwd=(.*?);(.*)"
    
    match = re.match(pattern, ms_conn_str)
    if match:
        driver = match.group(1)
        server = match.group(2)
        database = match.group(3)
        username = match.group(4)
        password = match.group(5)
        
        # Clean server string (remove "tcp:" if present)
        if server.startswith('tcp:'):
            server = server[4:]  # Remove "tcp:" prefix
        
        # Split the server and port by ',' (comma separator)
        if ',' in server:
            host, port = server.split(',', 1)
        else:
            host = server
            port = 1433  # Default port for SQL Server if not specified
        
        # Return the components
        return driver, host, port, database, username, password
    else:
        raise ValueError("Invalid MS SQL connection string format")

def build_sqlalchemy_uri(ms_conn_str):
    driver, host, port, database, username, password = parse_mssql_connection_string(ms_conn_str)
    
    # URL-encode the username and password
    username = quote_plus(username)
    password = quote_plus(password)
    
    # Construct the SQLAlchemy-compatible URI
    sqlalchemy_uri = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={quote_plus(driver)}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    
    return sqlalchemy_uri

def parse_redis_connection_string(redis_conn_str):
    # Regular expression pattern to extract the necessary components
    pattern = r"^(.*?):(\d+),password=([^,]+),(.*)$"
    
    match = re.match(pattern, redis_conn_str)
    if match:
        host = match.group(1)
        port = int(match.group(2)) 
        password = match.group(3) 
        options_str = match.group(4)

        options = {}
        for option in options_str.split(','):
            key, value = option.split('=')
            options[key] = value.strip()

        # Return the components
        return host, port, password, options

def build_redis_uri(redis_conn_str):
    host, port, password, options = parse_redis_connection_string(redis_conn_str)

    redis_uri = f"rediss://:{quote_plus(password)}@{host}:{port}"

    return redis_uri
