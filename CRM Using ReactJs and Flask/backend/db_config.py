import os

DB_CONFIG = {
    'DRIVER': os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
    'SERVER': os.environ.get('DB_SERVER', 'your_server'),
    'DATABASE': os.environ.get('DB_NAME', 'your_db'),
    'UID': os.environ.get('DB_USER', 'your_user'),
    'PWD': os.environ.get('DB_PASSWORD', 'your_password')
}

def get_connection_string():
    return (
        f"DRIVER={{{DB_CONFIG['DRIVER']}}};"
        f"SERVER={DB_CONFIG['SERVER']};"
        f"DATABASE={DB_CONFIG['DATABASE']};"
        f"UID={DB_CONFIG['UID']};"
        f"PWD={DB_CONFIG['PWD']}"
    )